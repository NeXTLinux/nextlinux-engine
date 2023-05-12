import threading
from types import TracebackType
from typing import Optional, Type

from sqlalchemy.orm import Session

<<<<<<< HEAD
from nextlinux_engine.clients.grype_wrapper import GrypeWrapperSingleton
from nextlinux_engine.clients.services import internal_client_for
from nextlinux_engine.clients.services.catalog import CatalogClient
from nextlinux_engine.db import GrypeDBFeedMetadata
from nextlinux_engine.db.db_grype_db_feed_metadata import (
    NoActiveGrypeDB,
    get_most_recent_active_grypedb,
)
from nextlinux_engine.services.policy_engine.engine.feeds.storage import (
    GrypeDBFile,
    GrypeDBStorage,
=======
from nextlinux_engine.clients.govulners_wrapper import GovulnersWrapperSingleton
from nextlinux_engine.clients.services import internal_client_for
from nextlinux_engine.clients.services.catalog import CatalogClient
from nextlinux_engine.db import GovulnersDBFeedMetadata
from nextlinux_engine.db.db_govulners_db_feed_metadata import (
    NoActiveGovulnersDB,
    get_most_recent_active_govulnersdb,
)
from nextlinux_engine.services.policy_engine.engine.feeds.storage import (
    GovulnersDBFile,
    GovulnersDBStorage,
>>>>>>> master
)
from nextlinux_engine.subsys import logger

LOCK_AQUISITION_TIMEOUT = 60


<<<<<<< HEAD
class GrypeDBSyncError(Exception):
    pass


class NoActiveDBSyncError(GrypeDBSyncError):
=======
class GovulnersDBSyncError(Exception):
    pass


class NoActiveDBSyncError(GovulnersDBSyncError):
>>>>>>> master
    def __init__(self):
        super().__init__("Local sync failed because no active db found in the database")


<<<<<<< HEAD
class GrypeDBSyncLockAquisitionTimeout(GrypeDBSyncError):
=======
class GovulnersDBSyncLockAquisitionTimeout(GovulnersDBSyncError):
>>>>>>> master
    def __init__(self, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Aquisition timeout of {self.timeout_seconds} seconds encountered before lock was released. Potential deadlock in system."
        )


<<<<<<< HEAD
class GrypeDBSyncLock:
=======
class GovulnersDBSyncLock:
>>>>>>> master
    _lock = threading.Lock()

    def __init__(self, timeout: int) -> None:
        self.timeout = timeout
        self.lock_acquired: bool = False

    def __enter__(self) -> None:
        self.lock_acquired = self._lock.acquire(timeout=self.timeout)
        if not self.lock_acquired:
<<<<<<< HEAD
            raise GrypeDBSyncLockAquisitionTimeout(self.timeout)
=======
            raise GovulnersDBSyncLockAquisitionTimeout(self.timeout)
>>>>>>> master

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.lock_acquired:
            self._lock.release()


<<<<<<< HEAD
class GrypeDBSyncManager:
    """
    Sync grype db to local instance of policy engine if it has been updated globally
    """

    @classmethod
    def _get_active_grypedb(cls, session) -> GrypeDBFeedMetadata:
=======
class GovulnersDBSyncManager:
    """
    Sync govulners db to local instance of policy engine if it has been updated globally
    """

    @classmethod
    def _get_active_govulnersdb(cls, session) -> GovulnersDBFeedMetadata:
>>>>>>> master
        """
        Uses dao to get the most recent active db, which should be the global active db
        If no active db, raises NoActiveDBSyncError
        """
        try:
<<<<<<< HEAD
            return get_most_recent_active_grypedb(session)
        except NoActiveGrypeDB:
            raise NoActiveDBSyncError

    @classmethod
    def _get_local_grypedb_checksum(cls) -> Optional[str]:
        """
        Returns checksum of grypedb on local instance

        return: Checksum of local grypedb
        rtype: str
        """
        # get local grypedb checksum
        # Wrapper raises ValueError if grypedb has not been initialized
        try:
            return GrypeWrapperSingleton.get_instance().get_current_grype_db_checksum()
=======
            return get_most_recent_active_govulnersdb(session)
        except NoActiveGovulnersDB:
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
            return GovulnersWrapperSingleton.get_instance().get_current_govulners_db_checksum()
>>>>>>> master
        except ValueError:
            return None

    @classmethod
<<<<<<< HEAD
    def _update_grypedb(
        cls,
        active_grypedb: GrypeDBFeedMetadata,
        grypedb_file_path: Optional[str] = None,
    ):
        """
        Runs GrypeDBSyncTask on instance. If file_path present, passes this to grype facade to update
        If not, it builds the catalog url, gets the raw document and saves it to tempfile and passes path to grype facade
        """
        try:
            if grypedb_file_path:
                cls._update_grypedb_wrapper(active_grypedb, grypedb_file_path)
            else:
                catalog_client = internal_client_for(CatalogClient, userId=None)
                bucket, archive_id = active_grypedb.object_url.split("/")[-2::]
                grypedb_document = catalog_client.get_raw_object(bucket, archive_id)

                # verify integrity of data, create tempfile, and pass path to facade
                GrypeDBFile.verify_integrity(
                    grypedb_document, active_grypedb.archive_checksum
                )
                with GrypeDBStorage() as grypedb_file:
                    with grypedb_file.create_file(active_grypedb.archive_checksum) as f:
                        f.write(grypedb_document)
                    cls._update_grypedb_wrapper(active_grypedb, grypedb_file.path)
        except Exception as e:
            logger.exception("GrypeDBSyncTask failed to sync")
            raise GrypeDBSyncError(str(e)) from e

    @staticmethod
    def _update_grypedb_wrapper(
        active_grypedb: GrypeDBFeedMetadata, grypedb_file_path: Optional[str] = None
    ):
        # Stage the new grype_db
        GrypeWrapperSingleton.get_instance().update_grype_db(
            grypedb_file_path,
            active_grypedb.archive_checksum,
            active_grypedb.schema_version,
=======
    def _update_govulnersdb(
        cls,
        active_govulnersdb: GovulnersDBFeedMetadata,
        govulnersdb_file_path: Optional[str] = None,
    ):
        """
        Runs GovulnersDBSyncTask on instance. If file_path present, passes this to govulners facade to update
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
                GovulnersDBFile.verify_integrity(
                    govulnersdb_document, active_govulnersdb.archive_checksum
                )
                with GovulnersDBStorage() as govulnersdb_file:
                    with govulnersdb_file.create_file(active_govulnersdb.archive_checksum) as f:
                        f.write(govulnersdb_document)
                    cls._update_govulnersdb_wrapper(active_govulnersdb, govulnersdb_file.path)
        except Exception as e:
            logger.exception("GovulnersDBSyncTask failed to sync")
            raise GovulnersDBSyncError(str(e)) from e

    @staticmethod
    def _update_govulnersdb_wrapper(
        active_govulnersdb: GovulnersDBFeedMetadata, govulnersdb_file_path: Optional[str] = None
    ):
        # Stage the new govulners_db
        GovulnersWrapperSingleton.get_instance().update_govulners_db(
            govulnersdb_file_path,
            active_govulnersdb.archive_checksum,
            active_govulnersdb.schema_version,
>>>>>>> master
            False,
        )

    @staticmethod
    def _is_sync_necessary(
<<<<<<< HEAD
        active_grypedb: GrypeDBFeedMetadata, local_grypedb_checksum: str
    ) -> bool:
        """
        Returns bool based upon comparisons between the active grype db and the local checksum passed to the function
        """
        if (
            not active_grypedb.archive_checksum
            or local_grypedb_checksum == active_grypedb.archive_checksum
        ):
            logger.info("No Grype DB sync needed at this time")
=======
        active_govulnersdb: GovulnersDBFeedMetadata, local_govulnersdb_checksum: str
    ) -> bool:
        """
        Returns bool based upon comparisons between the active govulners db and the local checksum passed to the function
        """
        if (
            not active_govulnersdb.archive_checksum
            or local_govulnersdb_checksum == active_govulnersdb.archive_checksum
        ):
            logger.info("No Govulners DB sync needed at this time")
>>>>>>> master
            return False

        return True

    @classmethod
<<<<<<< HEAD
    def run_grypedb_sync(
        cls, session: Session, grypedb_file_path: Optional[str] = None
    ):
        """
        Runs GrypeDBSyncTask if it is necessary. Determines this by comparing local db checksum with active one in DB
=======
    def run_govulnersdb_sync(
        cls, session: Session, govulnersdb_file_path: Optional[str] = None
    ):
        """
        Runs GovulnersDBSyncTask if it is necessary. Determines this by comparing local db checksum with active one in DB
>>>>>>> master
        Returns true or false based upon whether db updated
        *Note that this function may make commits on session object if there is more than one active db

        :param session: db session to be used for querying and commiting
<<<<<<< HEAD
        :param grypedb_file_path: Can be passed a fie path to existing grypedb to use on local disk
=======
        :param govulnersdb_file_path: Can be passed a fie path to existing govulnersdb to use on local disk
>>>>>>> master
        return: Boolean to whether the db was updated or not
        rtype: bool
        """
        # Do an initial check outside of lock to determine if sync is necessary
        # Helps ensure that synchronous processes are not slowed by lock
<<<<<<< HEAD
        active_grypedb = cls._get_active_grypedb(session)
        local_grypedb_checksum = cls._get_local_grypedb_checksum()
        is_sync_necessary = cls._is_sync_necessary(
            active_grypedb, local_grypedb_checksum
=======
        active_govulnersdb = cls._get_active_govulnersdb(session)
        local_govulnersdb_checksum = cls._get_local_govulnersdb_checksum()
        is_sync_necessary = cls._is_sync_necessary(
            active_govulnersdb, local_govulnersdb_checksum
>>>>>>> master
        )
        if not is_sync_necessary:
            return False

<<<<<<< HEAD
        with GrypeDBSyncLock(LOCK_AQUISITION_TIMEOUT):
            # Need to requery and recheck the active an local checksums because data may have changed since waiting
            # on lock
            active_grypedb = cls._get_active_grypedb(session)
            local_grypedb_checksum = cls._get_local_grypedb_checksum()
            is_sync_necessary = cls._is_sync_necessary(
                active_grypedb, local_grypedb_checksum
=======
        with GovulnersDBSyncLock(LOCK_AQUISITION_TIMEOUT):
            # Need to requery and recheck the active an local checksums because data may have changed since waiting
            # on lock
            active_govulnersdb = cls._get_active_govulnersdb(session)
            local_govulnersdb_checksum = cls._get_local_govulnersdb_checksum()
            is_sync_necessary = cls._is_sync_necessary(
                active_govulnersdb, local_govulnersdb_checksum
>>>>>>> master
            )

            if is_sync_necessary:
                logger.info(
<<<<<<< HEAD
                    "Local policy engine updating local grype db with checksum of %s to the new globally active db with checksum %s",
                    local_grypedb_checksum,
                    active_grypedb.archive_checksum,
                )
                cls._update_grypedb(
                    active_grypedb=active_grypedb,
                    grypedb_file_path=grypedb_file_path,
=======
                    "Local policy engine updating local govulners db with checksum of %s to the new globally active db with checksum %s",
                    local_govulnersdb_checksum,
                    active_govulnersdb.archive_checksum,
                )
                cls._update_govulnersdb(
                    active_govulnersdb=active_govulnersdb,
                    govulnersdb_file_path=govulnersdb_file_path,
>>>>>>> master
                )
                return True
            else:
                return False
