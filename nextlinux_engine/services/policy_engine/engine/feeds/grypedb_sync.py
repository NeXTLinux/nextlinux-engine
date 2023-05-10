import threading
from types import TracebackType
from typing import Optional, Type

from sqlalchemy.orm import Session

from nextlinux_engine.clients.govulners_wrapper import GrypeWrapperSingleton
from nextlinux_engine.clients.services import internal_client_for
from nextlinux_engine.clients.services.catalog import CatalogClient
from nextlinux_engine.db import GrypeDBFeedMetadata
from nextlinux_engine.db.db_govulners_db_feed_metadata import (
    NoActiveGrypeDB,
    get_most_recent_active_govulnersdb,
)
from nextlinux_engine.services.policy_engine.engine.feeds.storage import (
    GrypeDBFile,
    GrypeDBStorage,
)
from nextlinux_engine.subsys import logger

LOCK_AQUISITION_TIMEOUT = 60


class GrypeDBSyncError(Exception):
    pass


class NoActiveDBSyncError(GrypeDBSyncError):
    def __init__(self):
        super().__init__("Local sync failed because no active db found in the database")


class GrypeDBSyncLockAquisitionTimeout(GrypeDBSyncError):
    def __init__(self, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Aquisition timeout of {self.timeout_seconds} seconds encountered before lock was released. Potential deadlock in system."
        )


class GrypeDBSyncLock:
    _lock = threading.Lock()

    def __init__(self, timeout: int) -> None:
        self.timeout = timeout
        self.lock_acquired: bool = False

    def __enter__(self) -> None:
        self.lock_acquired = self._lock.acquire(timeout=self.timeout)
        if not self.lock_acquired:
            raise GrypeDBSyncLockAquisitionTimeout(self.timeout)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.lock_acquired:
            self._lock.release()


class GrypeDBSyncManager:
    """
    Sync govulners db to local instance of policy engine if it has been updated globally
    """

    @classmethod
    def _get_active_govulnersdb(cls, session) -> GrypeDBFeedMetadata:
        """
        Uses dao to get the most recent active db, which should be the global active db
        If no active db, raises NoActiveDBSyncError
        """
        try:
            return get_most_recent_active_govulnersdb(session)
        except NoActiveGrypeDB:
            raise NoActiveDBSyncError

    @classmethod
    def _get_local_govulnersdb_checksum(cls) -> Optional[str]:
        """
        Returns checksum of govulnersdb on local instance

        return: Checksum of local govulnersdb
        rtype: str
        """
        # get local govulnersdb checksum
        # Wrapper raises ValueError if govulnersdb has not been initialized
        try:
            return GrypeWrapperSingleton.get_instance().get_current_govulners_db_checksum()
        except ValueError:
            return None

    @classmethod
    def _update_govulnersdb(
        cls,
        active_govulnersdb: GrypeDBFeedMetadata,
        govulnersdb_file_path: Optional[str] = None,
    ):
        """
        Runs GrypeDBSyncTask on instance. If file_path present, passes this to govulners facade to update
        If not, it builds the catalog url, gets the raw document and saves it to tempfile and passes path to govulners facade
        """
        try:
            if govulnersdb_file_path:
                cls._update_govulnersdb_wrapper(active_govulnersdb, govulnersdb_file_path)
            else:
                catalog_client = internal_client_for(CatalogClient, userId=None)
                bucket, archive_id = active_govulnersdb.object_url.split("/")[-2::]
                govulnersdb_document = catalog_client.get_raw_object(bucket, archive_id)

                # verify integrity of data, create tempfile, and pass path to facade
                GrypeDBFile.verify_integrity(
                    govulnersdb_document, active_govulnersdb.archive_checksum
                )
                with GrypeDBStorage() as govulnersdb_file:
                    with govulnersdb_file.create_file(active_govulnersdb.archive_checksum) as f:
                        f.write(govulnersdb_document)
                    cls._update_govulnersdb_wrapper(active_govulnersdb, govulnersdb_file.path)
        except Exception as e:
            logger.exception("GrypeDBSyncTask failed to sync")
            raise GrypeDBSyncError(str(e)) from e

    @staticmethod
    def _update_govulnersdb_wrapper(
        active_govulnersdb: GrypeDBFeedMetadata, govulnersdb_file_path: Optional[str] = None
    ):
        # Stage the new govulners_db
        GrypeWrapperSingleton.get_instance().update_govulners_db(
            govulnersdb_file_path,
            active_govulnersdb.archive_checksum,
            active_govulnersdb.schema_version,
            False,
        )

    @staticmethod
    def _is_sync_necessary(
        active_govulnersdb: GrypeDBFeedMetadata, local_govulnersdb_checksum: str
    ) -> bool:
        """
        Returns bool based upon comparisons between the active govulners db and the local checksum passed to the function
        """
        if (
            not active_govulnersdb.archive_checksum
            or local_govulnersdb_checksum == active_govulnersdb.archive_checksum
        ):
            logger.info("No Grype DB sync needed at this time")
            return False

        return True

    @classmethod
    def run_govulnersdb_sync(
        cls, session: Session, govulnersdb_file_path: Optional[str] = None
    ):
        """
        Runs GrypeDBSyncTask if it is necessary. Determines this by comparing local db checksum with active one in DB
        Returns true or false based upon whether db updated
        *Note that this function may make commits on session object if there is more than one active db

        :param session: db session to be used for querying and commiting
        :param govulnersdb_file_path: Can be passed a fie path to existing govulnersdb to use on local disk
        return: Boolean to whether the db was updated or not
        rtype: bool
        """
        # Do an initial check outside of lock to determine if sync is necessary
        # Helps ensure that synchronous processes are not slowed by lock
        active_govulnersdb = cls._get_active_govulnersdb(session)
        local_govulnersdb_checksum = cls._get_local_govulnersdb_checksum()
        is_sync_necessary = cls._is_sync_necessary(
            active_govulnersdb, local_govulnersdb_checksum
        )
        if not is_sync_necessary:
            return False

        with GrypeDBSyncLock(LOCK_AQUISITION_TIMEOUT):
            # Need to requery and recheck the active an local checksums because data may have changed since waiting
            # on lock
            active_govulnersdb = cls._get_active_govulnersdb(session)
            local_govulnersdb_checksum = cls._get_local_govulnersdb_checksum()
            is_sync_necessary = cls._is_sync_necessary(
                active_govulnersdb, local_govulnersdb_checksum
            )

            if is_sync_necessary:
                logger.info(
                    "Local policy engine updating local govulners db with checksum of %s to the new globally active db with checksum %s",
                    local_govulnersdb_checksum,
                    active_govulnersdb.archive_checksum,
                )
                cls._update_govulnersdb(
                    active_govulnersdb=active_govulnersdb,
                    govulnersdb_file_path=govulnersdb_file_path,
                )
                return True
            else:
                return False
