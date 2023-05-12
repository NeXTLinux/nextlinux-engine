import errno
import json
import os
import shlex
import shutil
import tarfile
from contextlib import contextmanager
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Dict, Iterable, List, Optional, Tuple

import sqlalchemy
from readerwriterlock import rwlock
from sqlalchemy import Column, ForeignKey, Integer, String, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import nextlinux_engine.configuration.localconfig
from nextlinux_engine.db.entities.common import UtilMixin
from nextlinux_engine.subsys import logger
from nextlinux_engine.utils import CommandException, run_check

VULNERABILITIES = "vulnerabilities"
VULNERABILITY_TABLE_NAME = "vulnerability"
VULNERABILITY_METADATA_TABLE_NAME = "vulnerability_metadata"
Base = declarative_base()


# Table definitions.
<<<<<<< HEAD
class GrypeVulnerability(Base, UtilMixin):
=======
class GovulnersVulnerability(Base, UtilMixin):
>>>>>>> master
    __tablename__ = VULNERABILITY_TABLE_NAME

    pk = Column(Integer, primary_key=True)
    id = Column(String)
    package_name = Column(String)
    namespace = Column(String)
    version_constraint = Column(String)
    version_format = Column(String)
    cpes = Column(String)
    related_vulnerabilities = Column(String)
    fixed_in_versions = Column(String)
    fix_state = Column(String)
    advisories = Column(String)

    @property
    def deserialized_related_vulnerabilities(self):
        return json.loads(self.related_vulnerabilities)

    @property
    def deserialized_fixed_in_versions(self):
        return json.loads(self.fixed_in_versions)


<<<<<<< HEAD
class GrypeVulnerabilityMetadata(Base, UtilMixin):
=======
class GovulnersVulnerabilityMetadata(Base, UtilMixin):
>>>>>>> master
    __tablename__ = VULNERABILITY_METADATA_TABLE_NAME

    id = Column(String, ForeignKey(f"{VULNERABILITY_TABLE_NAME}.id"), primary_key=True)
    namespace = Column(String, primary_key=True)
    data_source = Column(String)
    record_source = Column(String)
    severity = Column(String)
    urls = Column(String)
    description = Column(String)
    cvss = Column(String)

    @property
    def deserialized_urls(self):
        return json.loads(self.urls)

    @property
    def deserialized_cvss(self):
        return json.loads(self.cvss)


@dataclass
<<<<<<< HEAD
class GrypeDBMetadata:
=======
class GovulnersDBMetadata:
>>>>>>> master
    built: str
    version: str
    checksum: str

    @staticmethod
    def to_object(db_metadata: dict):
        """
<<<<<<< HEAD
        Convert a dict object into a GrypeDBMetadata
        """
        return GrypeDBMetadata(**db_metadata)


@dataclass
class GrypeDBEngineMetadata:
    db_checksum: str
    archive_checksum: str
    grype_db_version: str
=======
        Convert a dict object into a GovulnersDBMetadata
        """
        return GovulnersDBMetadata(**db_metadata)


@dataclass
class GovulnersDBEngineMetadata:
    db_checksum: str
    archive_checksum: str
    govulners_db_version: str
>>>>>>> master

    @staticmethod
    def to_object(engine_metadata: dict):
        """
<<<<<<< HEAD
        Convert a dict object into a GrypeEngineMetadata
        """
        return GrypeDBEngineMetadata(**engine_metadata)
=======
        Convert a dict object into a GovulnersEngineMetadata
        """
        return GovulnersDBEngineMetadata(**engine_metadata)
>>>>>>> master


@dataclass
class RecordSource:
    count: int
    feed: str
    group: str
    last_synced: str


class LockAcquisitionError(Exception):
    pass


<<<<<<< HEAD
class GrypeWrapperSingleton(object):
    _grype_wrapper_instance = None
=======
class GovulnersWrapperSingleton(object):
    _govulners_wrapper_instance = None
>>>>>>> master

    # These values should be treated as constants, and will not be changed by the functions below
    LOCK_READ_ACCESS_TIMEOUT = 60000
    LOCK_WRITE_ACCESS_TIMEOUT = 60000
    SQL_LITE_URL_TEMPLATE = "sqlite:///{}"
<<<<<<< HEAD
    GRYPE_SUB_COMMAND = "grype -vv -o json"
    GRYPE_VERSION_COMMAND = "grype version -o json"
    VULNERABILITY_FILE_NAME = "vulnerability.db"
    METADATA_FILE_NAME = "metadata.json"
    ENGINE_METADATA_FILE_NAME = "engine_metadata.json"
    ARCHIVE_FILE_NOT_FOUND_ERROR_MESSAGE = "New grype_db archive file not found"
    STAGED_GRYPE_DB_NOT_FOUND_ERROR_MESSAGE = "Unable to promote staged grype_db with archive checksum %s because it was not found."
    GRYPE_BASE_ENV_VARS = {
        "GRYPE_CHECK_FOR_APP_UPDATE": "0",
        "GRYPE_LOG_STRUCTURED": "1",
        "GRYPE_DB_AUTO_UPDATE": "0",
    }
    MISSING_GRYPE_DB_DIR_ERROR_MESSAGE = (
        "Cannot access missing grype_db dir. Reinitialize grype_db."
    )
    MISSING_GRYPE_DB_VERSION_ERROR_MESSAGE = (
        "Cannot access missing grype_db version. Reinitialize grype_db."
    )
    MISSING_GRYPE_DB_SESSION_MAKER_ERROR_MESSAGE = (
        "Cannot access missing grype_db session maker. Reinitialize grype_db."
=======
    GOVULNERS_SUB_COMMAND = "govulners -vv -o json"
    GOVULNERS_VERSION_COMMAND = "govulners version -o json"
    VULNERABILITY_FILE_NAME = "vulnerability.db"
    METADATA_FILE_NAME = "metadata.json"
    ENGINE_METADATA_FILE_NAME = "engine_metadata.json"
    ARCHIVE_FILE_NOT_FOUND_ERROR_MESSAGE = "New govulners_db archive file not found"
    STAGED_GOVULNERS_DB_NOT_FOUND_ERROR_MESSAGE = "Unable to promote staged govulners_db with archive checksum %s because it was not found."
    GOVULNERS_BASE_ENV_VARS = {
        "GOVULNERS_CHECK_FOR_APP_UPDATE": "0",
        "GOVULNERS_LOG_STRUCTURED": "1",
        "GOVULNERS_DB_AUTO_UPDATE": "0",
    }
    MISSING_GOVULNERS_DB_DIR_ERROR_MESSAGE = (
        "Cannot access missing govulners_db dir. Reinitialize govulners_db."
    )
    MISSING_GOVULNERS_DB_VERSION_ERROR_MESSAGE = (
        "Cannot access missing govulners_db version. Reinitialize govulners_db."
    )
    MISSING_GOVULNERS_DB_SESSION_MAKER_ERROR_MESSAGE = (
        "Cannot access missing govulners_db session maker. Reinitialize govulners_db."
>>>>>>> master
    )

    def __new__(cls):
        # If the singleton has not been initialized yet, do so with the instance variables below
<<<<<<< HEAD
        if cls._grype_wrapper_instance is None:
            logger.debug("Initializing Grype wrapper instance.")
            # The singleton instance, only instantiated once outside of testing
            cls._grype_wrapper_instance = super(GrypeWrapperSingleton, cls).__new__(cls)

            # These variables are mutable, their state can be changed when grype_db is updated
            cls._grype_db_dir_internal = None
            cls._grype_db_version_internal = None
            cls._grype_db_session_maker_internal = None

            # These variables are also mutable. They are for staging updated grye_dbs.
            cls._staging_grype_db_dir_internal = None
            cls._staging_grype_db_version_internal = None
            cls._staging_grype_db_session_maker_internal = None

            # The reader-writer lock for this class
            cls._grype_db_lock = rwlock.RWLockWrite()

        # Return the singleton instance
        return cls._grype_wrapper_instance
=======
        if cls._govulners_wrapper_instance is None:
            logger.debug("Initializing Govulners wrapper instance.")
            # The singleton instance, only instantiated once outside of testing
            cls._govulners_wrapper_instance = super(GovulnersWrapperSingleton, cls).__new__(cls)

            # These variables are mutable, their state can be changed when govulners_db is updated
            cls._govulners_db_dir_internal = None
            cls._govulners_db_version_internal = None
            cls._govulners_db_session_maker_internal = None

            # These variables are also mutable. They are for staging updated grye_dbs.
            cls._staging_govulners_db_dir_internal = None
            cls._staging_govulners_db_version_internal = None
            cls._staging_govulners_db_session_maker_internal = None

            # The reader-writer lock for this class
            cls._govulners_db_lock = rwlock.RWLockWrite()

        # Return the singleton instance
        return cls._govulners_wrapper_instance
>>>>>>> master

    @classmethod
    def get_instance(cls):
        """
        Returns the singleton instance of this class.
        """
<<<<<<< HEAD
        return GrypeWrapperSingleton()

    @property
    def _grype_db_dir(self):
        if self._grype_db_dir_internal is None:
            raise ValueError(self.MISSING_GRYPE_DB_DIR_ERROR_MESSAGE)
        else:
            return self._grype_db_dir_internal

    @_grype_db_dir.setter
    def _grype_db_dir(self, grype_db_dir_internal):
        self._grype_db_dir_internal = grype_db_dir_internal

    @property
    def _grype_db_version(self):
        if self._grype_db_version_internal is None:
            raise ValueError(self.MISSING_GRYPE_DB_VERSION_ERROR_MESSAGE)
        else:
            return self._grype_db_version_internal

    @_grype_db_version.setter
    def _grype_db_version(self, grype_db_version_internal):
        self._grype_db_version_internal = grype_db_version_internal

    @property
    def _grype_db_session_maker(self):
        if self._grype_db_session_maker_internal is None:
            raise ValueError(self.MISSING_GRYPE_DB_SESSION_MAKER_ERROR_MESSAGE)
        else:
            return self._grype_db_session_maker_internal

    @_grype_db_session_maker.setter
    def _grype_db_session_maker(self, grype_db_session_maker_internal):
        self._grype_db_session_maker_internal = grype_db_session_maker_internal

    @property
    def _staging_grype_db_dir(self):
        return self._staging_grype_db_dir_internal

    @_staging_grype_db_dir.setter
    def _staging_grype_db_dir(self, staging_grype_db_dir_internal):
        self._staging_grype_db_dir_internal = staging_grype_db_dir_internal

    @property
    def _staging_grype_db_version(self):
        return self._staging_grype_db_version_internal

    @_staging_grype_db_version.setter
    def _staging_grype_db_version(self, staging_grype_db_version_internal):
        self._staging_grype_db_version_internal = staging_grype_db_version_internal

    @property
    def _staging_grype_db_session_maker(self):
        return self._staging_grype_db_session_maker_internal

    @_staging_grype_db_session_maker.setter
    def _staging_grype_db_session_maker(self, staging_grype_db_session_maker_internal):
        self._staging_grype_db_session_maker_internal = (
            staging_grype_db_session_maker_internal
=======
        return GovulnersWrapperSingleton()

    @property
    def _govulners_db_dir(self):
        if self._govulners_db_dir_internal is None:
            raise ValueError(self.MISSING_GOVULNERS_DB_DIR_ERROR_MESSAGE)
        else:
            return self._govulners_db_dir_internal

    @_govulners_db_dir.setter
    def _govulners_db_dir(self, govulners_db_dir_internal):
        self._govulners_db_dir_internal = govulners_db_dir_internal

    @property
    def _govulners_db_version(self):
        if self._govulners_db_version_internal is None:
            raise ValueError(self.MISSING_GOVULNERS_DB_VERSION_ERROR_MESSAGE)
        else:
            return self._govulners_db_version_internal

    @_govulners_db_version.setter
    def _govulners_db_version(self, govulners_db_version_internal):
        self._govulners_db_version_internal = govulners_db_version_internal

    @property
    def _govulners_db_session_maker(self):
        if self._govulners_db_session_maker_internal is None:
            raise ValueError(self.MISSING_GOVULNERS_DB_SESSION_MAKER_ERROR_MESSAGE)
        else:
            return self._govulners_db_session_maker_internal

    @_govulners_db_session_maker.setter
    def _govulners_db_session_maker(self, govulners_db_session_maker_internal):
        self._govulners_db_session_maker_internal = govulners_db_session_maker_internal

    @property
    def _staging_govulners_db_dir(self):
        return self._staging_govulners_db_dir_internal

    @_staging_govulners_db_dir.setter
    def _staging_govulners_db_dir(self, staging_govulners_db_dir_internal):
        self._staging_govulners_db_dir_internal = staging_govulners_db_dir_internal

    @property
    def _staging_govulners_db_version(self):
        return self._staging_govulners_db_version_internal

    @_staging_govulners_db_version.setter
    def _staging_govulners_db_version(self, staging_govulners_db_version_internal):
        self._staging_govulners_db_version_internal = staging_govulners_db_version_internal

    @property
    def _staging_govulners_db_session_maker(self):
        return self._staging_govulners_db_session_maker_internal

    @_staging_govulners_db_session_maker.setter
    def _staging_govulners_db_session_maker(self, staging_govulners_db_session_maker_internal):
        self._staging_govulners_db_session_maker_internal = (
            staging_govulners_db_session_maker_internal
>>>>>>> master
        )

    @contextmanager
    def read_lock_access(self):
        """
        Get read access to the reader writer lock. Releases the lock after exit the
        context. Any exceptions are passed up.
        """
<<<<<<< HEAD
        logger.debug("Attempting to get read access for the grype_db lock")
        read_lock = self._grype_db_lock.gen_rlock()

        try:
            if read_lock.acquire(timeout=self.LOCK_READ_ACCESS_TIMEOUT):
                logger.debug("Acquired read access for the grype_db lock")
                yield
            else:
                raise LockAcquisitionError(
                    "Unable to acquire read access for the grype_db lock"
                )
        finally:
            if read_lock.locked():
                logger.debug("Releasing read access for the grype_db lock")
=======
        logger.debug("Attempting to get read access for the govulners_db lock")
        read_lock = self._govulners_db_lock.gen_rlock()

        try:
            if read_lock.acquire(timeout=self.LOCK_READ_ACCESS_TIMEOUT):
                logger.debug("Acquired read access for the govulners_db lock")
                yield
            else:
                raise LockAcquisitionError(
                    "Unable to acquire read access for the govulners_db lock"
                )
        finally:
            if read_lock.locked():
                logger.debug("Releasing read access for the govulners_db lock")
>>>>>>> master
                read_lock.release()

    @contextmanager
    def write_lock_access(self):
        """
        Get read access to the reader writer lock. Releases the lock after exit the
        context. y exceptions are passed up.
        """
<<<<<<< HEAD
        logger.debug("Attempting to get write access for the grype_db lock")
        write_lock = self._grype_db_lock.gen_wlock()

        try:
            if write_lock.acquire(timeout=self.LOCK_READ_ACCESS_TIMEOUT):
                logger.debug("Unable to acquire write access for the grype_db lock")
                yield
            else:
                raise LockAcquisitionError(
                    "Unable to acquire write access for the grype_db lock"
                )
        finally:
            if write_lock.locked():
                logger.debug("Releasing write access for the grype_db lock")
                write_lock.release()

    @contextmanager
    def grype_session_scope(self, use_staging: bool = False):
        """
        Provides simplified session scope management around the currently configured grype db. Grype
=======
        logger.debug("Attempting to get write access for the govulners_db lock")
        write_lock = self._govulners_db_lock.gen_wlock()

        try:
            if write_lock.acquire(timeout=self.LOCK_READ_ACCESS_TIMEOUT):
                logger.debug("Unable to acquire write access for the govulners_db lock")
                yield
            else:
                raise LockAcquisitionError(
                    "Unable to acquire write access for the govulners_db lock"
                )
        finally:
            if write_lock.locked():
                logger.debug("Releasing write access for the govulners_db lock")
                write_lock.release()

    @contextmanager
    def govulners_session_scope(self, use_staging: bool = False):
        """
        Provides simplified session scope management around the currently configured govulners db. Govulners
>>>>>>> master
        wrapper only reads from this db (writes only ever happen upstream when the db file is created!)
        so there's no need for normal transaction management as there will never be changes to commit.
        This context manager primarily ensures the session is closed after use.
        """
        if use_staging:
<<<<<<< HEAD
            session = self._staging_grype_db_session_maker()
        else:
            session = self._grype_db_session_maker()

        logger.debug("Opening grype_db session: " + str(session))
=======
            session = self._staging_govulners_db_session_maker()
        else:
            session = self._govulners_db_session_maker()

        logger.debug("Opening govulners_db session: " + str(session))
>>>>>>> master
        try:
            yield session
        except Exception as exception:
            raise exception
        finally:
<<<<<<< HEAD
            logger.debug("Closing grype_db session: " + str(session))
=======
            logger.debug("Closing govulners_db session: " + str(session))
>>>>>>> master
            session.close()

    @staticmethod
    def read_file_to_json(file_path: str) -> json:
        """
        Static helper function that accepts a file path, ensures it exists, and then reads the contents as json.
        This logs an error and returns None if the file does not exist or cannot be parsed into json, otherwise
        it returns the json.
        """
        # If the file does not exist, log an error and return None
        if not os.path.exists(file_path):
            logger.error(
                "Unable to read non-exists file at %s to json.",
                file_path,
            )
            return None
        else:
            # Get the contents of the file
            with open(file_path) as read_file:
                try:
                    return json.load(read_file)
                except JSONDecodeError:
                    logger.error(
                        "Unable to parse file at %s into json.",
                        file_path,
                    )
                    return None

<<<<<<< HEAD
    def get_current_grype_db_checksum(self):
        """
        Return the checksum for the in-use version of grype db from the dir base name
        """
        if self._grype_db_dir and os.path.exists(self._grype_db_dir):
            grype_db_checksum = os.path.basename(self._grype_db_dir)
        else:
            grype_db_checksum = None
        logger.info("Returning current grype_db checksum: %s", grype_db_checksum)
        return grype_db_checksum

    @staticmethod
    def _get_default_grype_db_dir_from_config():
        """
        Get the default grype db dir from config, and create it if it does not exist.
        """
        localconfig = nextlinux_engine.configuration.localconfig.get_config()
        if "grype_db_dir" in localconfig:
            local_grype_db_dir = os.path.join(
                localconfig["service_dir"], localconfig["grype_db_dir"]
            )
        else:
            local_grype_db_dir = os.path.join(localconfig["service_dir"], "grype_db/")

        if not os.path.exists(local_grype_db_dir):
            os.mkdir(local_grype_db_dir)

        return local_grype_db_dir

    def _move_grype_db_archive(
        self, grype_db_archive_local_file_location: str, output_dir: str
    ) -> str:
        # Get the location to move the archive to
        archive_file_name = os.path.basename(grype_db_archive_local_file_location)
        grype_db_archive_copied_file_location = os.path.join(
            output_dir, archive_file_name
        )

        if not os.path.exists(grype_db_archive_local_file_location):
            logger.warn(
                "Unable to move grype_db archive from %s to %s because it does not exist",
                grype_db_archive_local_file_location,
                grype_db_archive_copied_file_location,
=======
    def get_current_govulners_db_checksum(self):
        """
        Return the checksum for the in-use version of govulners db from the dir base name
        """
        if self._govulners_db_dir and os.path.exists(self._govulners_db_dir):
            govulners_db_checksum = os.path.basename(self._govulners_db_dir)
        else:
            govulners_db_checksum = None
        logger.info("Returning current govulners_db checksum: %s", govulners_db_checksum)
        return govulners_db_checksum

    @staticmethod
    def _get_default_govulners_db_dir_from_config():
        """
        Get the default govulners db dir from config, and create it if it does not exist.
        """
        localconfig = nextlinux_engine.configuration.localconfig.get_config()
        if "govulners_db_dir" in localconfig:
            local_govulners_db_dir = os.path.join(
                localconfig["service_dir"], localconfig["govulners_db_dir"]
            )
        else:
            local_govulners_db_dir = os.path.join(localconfig["service_dir"], "govulners_db/")

        if not os.path.exists(local_govulners_db_dir):
            os.mkdir(local_govulners_db_dir)

        return local_govulners_db_dir

    def _move_govulners_db_archive(
        self, govulners_db_archive_local_file_location: str, output_dir: str
    ) -> str:
        # Get the location to move the archive to
        archive_file_name = os.path.basename(govulners_db_archive_local_file_location)
        govulners_db_archive_copied_file_location = os.path.join(
            output_dir, archive_file_name
        )

        if not os.path.exists(govulners_db_archive_local_file_location):
            logger.warn(
                "Unable to move govulners_db archive from %s to %s because it does not exist",
                govulners_db_archive_local_file_location,
                govulners_db_archive_copied_file_location,
>>>>>>> master
            )
            raise FileNotFoundError(
                errno.ENOENT,
                self.ARCHIVE_FILE_NOT_FOUND_ERROR_MESSAGE,
<<<<<<< HEAD
                grype_db_archive_local_file_location,
=======
                govulners_db_archive_local_file_location,
>>>>>>> master
            )
        else:
            # Move the archive file
            logger.info(
<<<<<<< HEAD
                "Moving the grype_db archive from %s to %s",
                grype_db_archive_local_file_location,
                grype_db_archive_copied_file_location,
            )
            shutil.copyfile(
                grype_db_archive_local_file_location,
                grype_db_archive_copied_file_location,
            )
            return grype_db_archive_copied_file_location

    def _open_grype_db_archive(
        self,
        grype_db_archive_copied_file_location: str,
        parent_dir: str,
        archive_checksum: str,
        grype_db_version: str,
    ) -> str:
        grype_db_parent_dir = os.path.join(parent_dir, archive_checksum)
        grype_db_versioned_dir = os.path.join(grype_db_parent_dir, grype_db_version)
        if not os.path.exists(grype_db_versioned_dir):
            os.makedirs(grype_db_versioned_dir)

        logger.info(
            "Unpacking the grype_db archive with checksum: %s and db version: %s at %s into %s",
            archive_checksum,
            grype_db_version,
            grype_db_archive_copied_file_location,
            grype_db_parent_dir,
        )

        # Put the extracted files in the versioned dir
        with tarfile.open(grype_db_archive_copied_file_location) as read_archive:
            read_archive.extractall(grype_db_versioned_dir)

        # Return the full path to the parent grype_db dir. This is the dir we actually pass to grype,
        # which expects the version subdirectory to be under it.
        logger.info("Returning the unpacked grype_db dir at %s", grype_db_parent_dir)
        return grype_db_parent_dir

    def _write_engine_metadata_to_file(
        self, latest_grype_db_dir: str, archive_checksum: str, grype_db_version: str
    ):
        """
        Write engine metadata to file. This file will contain a json with the values
        for archive_checksum and grype_db_version for the current;y configured grype_db.

        This method writes that file to the same dir the grype_db archive was unpacked at
        in _open_grype_db_archive(). This means that it assumes the dir already exists,
=======
                "Moving the govulners_db archive from %s to %s",
                govulners_db_archive_local_file_location,
                govulners_db_archive_copied_file_location,
            )
            shutil.copyfile(
                govulners_db_archive_local_file_location,
                govulners_db_archive_copied_file_location,
            )
            return govulners_db_archive_copied_file_location

    def _open_govulners_db_archive(
        self,
        govulners_db_archive_copied_file_location: str,
        parent_dir: str,
        archive_checksum: str,
        govulners_db_version: str,
    ) -> str:
        govulners_db_parent_dir = os.path.join(parent_dir, archive_checksum)
        govulners_db_versioned_dir = os.path.join(govulners_db_parent_dir, govulners_db_version)
        if not os.path.exists(govulners_db_versioned_dir):
            os.makedirs(govulners_db_versioned_dir)

        logger.info(
            "Unpacking the govulners_db archive with checksum: %s and db version: %s at %s into %s",
            archive_checksum,
            govulners_db_version,
            govulners_db_archive_copied_file_location,
            govulners_db_parent_dir,
        )

        # Put the extracted files in the versioned dir
        with tarfile.open(govulners_db_archive_copied_file_location) as read_archive:
            read_archive.extractall(govulners_db_versioned_dir)

        # Return the full path to the parent govulners_db dir. This is the dir we actually pass to govulners,
        # which expects the version subdirectory to be under it.
        logger.info("Returning the unpacked govulners_db dir at %s", govulners_db_parent_dir)
        return govulners_db_parent_dir

    def _write_engine_metadata_to_file(
        self, latest_govulners_db_dir: str, archive_checksum: str, govulners_db_version: str
    ):
        """
        Write engine metadata to file. This file will contain a json with the values
        for archive_checksum and govulners_db_version for the current;y configured govulners_db.

        This method writes that file to the same dir the govulners_db archive was unpacked at
        in _open_govulners_db_archive(). This means that it assumes the dir already exists,
>>>>>>> master
        and does not check to see if it needs to be created prior to writing to it.
        """
        # Get the db checksum and add it below
        metadata_file = os.path.join(
<<<<<<< HEAD
            latest_grype_db_dir, grype_db_version, self.METADATA_FILE_NAME
=======
            latest_govulners_db_dir, govulners_db_version, self.METADATA_FILE_NAME
>>>>>>> master
        )
        db_checksum = None
        if metadata := self.read_file_to_json(metadata_file):
            db_checksum = metadata.get("checksum", None)

<<<<<<< HEAD
        # Write the engine metadata file in the same dir as the ret of the grype db files
        output_file = os.path.join(
            latest_grype_db_dir, grype_db_version, self.ENGINE_METADATA_FILE_NAME
=======
        # Write the engine metadata file in the same dir as the ret of the govulners db files
        output_file = os.path.join(
            latest_govulners_db_dir, govulners_db_version, self.ENGINE_METADATA_FILE_NAME
>>>>>>> master
        )

        # Assemble the engine metadata json
        engine_metadata = {
            "archive_checksum": archive_checksum,
            "db_checksum": db_checksum,
<<<<<<< HEAD
            "grype_db_version": grype_db_version,
=======
            "govulners_db_version": govulners_db_version,
>>>>>>> master
        }

        # Write engine_metadata to file at output_file
        with open(output_file, "w") as write_file:
            json.dump(engine_metadata, write_file)

        return

<<<<<<< HEAD
    def _remove_grype_db_archive(self, grype_db_archive_local_file_location: str):
        logger.info(
            "Removing the now-unpacked grype_db archive at %s",
            grype_db_archive_local_file_location,
        )
        os.remove(grype_db_archive_local_file_location)

    def _move_and_open_grype_db_archive(
        self,
        grype_db_archive_local_file_location: str,
        archive_checksum: str,
        grype_db_version: str,
    ) -> str:
        """
        This function moves a tarball containing the latest grype db from a location on the local file system
        into the configured grype db dir. It then extracts all files in the tarball and removes the then-unneeded
        archive file.
        """
        # Get the location to copy the archive to
        local_db_dir = self._get_default_grype_db_dir_from_config()

        # Move the archive
        grype_db_archive_copied_file_location = self._move_grype_db_archive(
            grype_db_archive_local_file_location, local_db_dir
        )

        # Unpack the archive
        latest_grype_db_dir = self._open_grype_db_archive(
            grype_db_archive_copied_file_location,
            local_db_dir,
            archive_checksum,
            grype_db_version,
        )

        # Remove the unpacked archive
        self._remove_grype_db_archive(grype_db_archive_copied_file_location)

        # Store the archive_checksum and grype_db_version version in their own metadata file
        self._write_engine_metadata_to_file(
            latest_grype_db_dir, archive_checksum, grype_db_version
        )

        # Return the full path to the grype db file
        return latest_grype_db_dir

    def _init_latest_grype_db_engine(
        self, latest_grype_db_dir: str, grype_db_version: str
=======
    def _remove_govulners_db_archive(self, govulners_db_archive_local_file_location: str):
        logger.info(
            "Removing the now-unpacked govulners_db archive at %s",
            govulners_db_archive_local_file_location,
        )
        os.remove(govulners_db_archive_local_file_location)

    def _move_and_open_govulners_db_archive(
        self,
        govulners_db_archive_local_file_location: str,
        archive_checksum: str,
        govulners_db_version: str,
    ) -> str:
        """
        This function moves a tarball containing the latest govulners db from a location on the local file system
        into the configured govulners db dir. It then extracts all files in the tarball and removes the then-unneeded
        archive file.
        """
        # Get the location to copy the archive to
        local_db_dir = self._get_default_govulners_db_dir_from_config()

        # Move the archive
        govulners_db_archive_copied_file_location = self._move_govulners_db_archive(
            govulners_db_archive_local_file_location, local_db_dir
        )

        # Unpack the archive
        latest_govulners_db_dir = self._open_govulners_db_archive(
            govulners_db_archive_copied_file_location,
            local_db_dir,
            archive_checksum,
            govulners_db_version,
        )

        # Remove the unpacked archive
        self._remove_govulners_db_archive(govulners_db_archive_copied_file_location)

        # Store the archive_checksum and govulners_db_version version in their own metadata file
        self._write_engine_metadata_to_file(
            latest_govulners_db_dir, archive_checksum, govulners_db_version
        )

        # Return the full path to the govulners db file
        return latest_govulners_db_dir

    def _init_latest_govulners_db_engine(
        self, latest_govulners_db_dir: str, govulners_db_version: str
>>>>>>> master
    ) -> sqlalchemy.engine:
        """
        Create and return the sqlalchemy engine object
        """
        logger.info(
<<<<<<< HEAD
            "Creating new db engine based on the grype_db at %s", latest_grype_db_dir
        )
        latest_grype_db_file = os.path.join(
            latest_grype_db_dir, grype_db_version, self.VULNERABILITY_FILE_NAME
        )
        db_connect = self.SQL_LITE_URL_TEMPLATE.format(latest_grype_db_file)
        latest_grype_db_engine = sqlalchemy.create_engine(db_connect, echo=False)
        return latest_grype_db_engine

    def _init_latest_grype_db_session_maker(self, grype_db_engine) -> sessionmaker:
=======
            "Creating new db engine based on the govulners_db at %s", latest_govulners_db_dir
        )
        latest_govulners_db_file = os.path.join(
            latest_govulners_db_dir, govulners_db_version, self.VULNERABILITY_FILE_NAME
        )
        db_connect = self.SQL_LITE_URL_TEMPLATE.format(latest_govulners_db_file)
        latest_govulners_db_engine = sqlalchemy.create_engine(db_connect, echo=False)
        return latest_govulners_db_engine

    def _init_latest_govulners_db_session_maker(self, govulners_db_engine) -> sessionmaker:
>>>>>>> master
        """
        Create and return the db session maker
        """
        logger.info(
<<<<<<< HEAD
            "Creating new grype_db session maker from engine based on %s",
            grype_db_engine.url,
        )
        return sessionmaker(bind=grype_db_engine)

    def _init_latest_grype_db(
        self,
        lastest_grype_db_archive: str,
        archive_checksum: str,
        grype_db_version: str,
=======
            "Creating new govulners_db session maker from engine based on %s",
            govulners_db_engine.url,
        )
        return sessionmaker(bind=govulners_db_engine)

    def _init_latest_govulners_db(
        self,
        lastest_govulners_db_archive: str,
        archive_checksum: str,
        govulners_db_version: str,
>>>>>>> master
    ) -> Tuple[str, sessionmaker]:
        """
        Write the db string to file, create the engine, and create the session maker
        Return the file and session maker
        """
<<<<<<< HEAD
        latest_grype_db_dir = self._move_and_open_grype_db_archive(
            lastest_grype_db_archive, archive_checksum, grype_db_version
        )
        latest_grype_db_engine = self._init_latest_grype_db_engine(
            latest_grype_db_dir, grype_db_version
        )
        latest_grype_db_session_maker = self._init_latest_grype_db_session_maker(
            latest_grype_db_engine
        )

        # Return the dir and session maker
        return latest_grype_db_dir, latest_grype_db_session_maker

    def _remove_local_grype_db(self, grype_db_dir) -> None:
        """
        Remove old the local grype db file
        """
        if os.path.exists(grype_db_dir):
            logger.info("Removing old grype_db at %s", grype_db_dir)
            shutil.rmtree(grype_db_dir)
        else:
            logger.warn(
                "Failed to remove grype db at %s as it cannot be found.", grype_db_dir
            )
        return

    def update_grype_db(
        self,
        grype_db_archive_local_file_location: str,
        archive_checksum: str,
        grype_db_version: str,
        use_staging: bool = False,
    ) -> Optional[GrypeDBEngineMetadata]:
        """
        Make an update to grype_db, using the provided archive file, archive checksum, and grype db version.
        use_staging determines if this is the active, production grype db used for scanning images and
=======
        latest_govulners_db_dir = self._move_and_open_govulners_db_archive(
            lastest_govulners_db_archive, archive_checksum, govulners_db_version
        )
        latest_govulners_db_engine = self._init_latest_govulners_db_engine(
            latest_govulners_db_dir, govulners_db_version
        )
        latest_govulners_db_session_maker = self._init_latest_govulners_db_session_maker(
            latest_govulners_db_engine
        )

        # Return the dir and session maker
        return latest_govulners_db_dir, latest_govulners_db_session_maker

    def _remove_local_govulners_db(self, govulners_db_dir) -> None:
        """
        Remove old the local govulners db file
        """
        if os.path.exists(govulners_db_dir):
            logger.info("Removing old govulners_db at %s", govulners_db_dir)
            shutil.rmtree(govulners_db_dir)
        else:
            logger.warn(
                "Failed to remove govulners db at %s as it cannot be found.", govulners_db_dir
            )
        return

    def update_govulners_db(
        self,
        govulners_db_archive_local_file_location: str,
        archive_checksum: str,
        govulners_db_version: str,
        use_staging: bool = False,
    ) -> Optional[GovulnersDBEngineMetadata]:
        """
        Make an update to govulners_db, using the provided archive file, archive checksum, and govulners db version.
        use_staging determines if this is the active, production govulners db used for scanning images and
>>>>>>> master
        querying vulnerability data, or if this is a staging db we are validating before promoting globally.

        Returns the engine metadata for upstream validation.
        """

        if use_staging:
            logger.info(
<<<<<<< HEAD
                "Updating the staging grype_db at %s to archive checksum %s",
                grype_db_archive_local_file_location,
=======
                "Updating the staging govulners_db at %s to archive checksum %s",
                govulners_db_archive_local_file_location,
>>>>>>> master
                archive_checksum,
            )
        else:
            logger.info(
<<<<<<< HEAD
                "Updating the production grype_db at %s to archive checksum %s",
                grype_db_archive_local_file_location,
=======
                "Updating the production govulners_db at %s to archive checksum %s",
                govulners_db_archive_local_file_location,
>>>>>>> master
                archive_checksum,
            )

        with self.write_lock_access():
            # Store the db locally and
            # Create the sqlalchemy session maker for the new db
            (
<<<<<<< HEAD
                latest_grype_db_dir,
                latest_grype_db_session_maker,
            ) = self._init_latest_grype_db(
                grype_db_archive_local_file_location, archive_checksum, grype_db_version
=======
                latest_govulners_db_dir,
                latest_govulners_db_session_maker,
            ) = self._init_latest_govulners_db(
                govulners_db_archive_local_file_location, archive_checksum, govulners_db_version
>>>>>>> master
            )

            # Store the staged dir and session variables
            if use_staging:
<<<<<<< HEAD
                self._staging_grype_db_dir = latest_grype_db_dir
                self._staging_grype_db_version = grype_db_version
                self._staging_grype_db_session_maker = latest_grype_db_session_maker

                logger.info(
                    "Staging grype_db updated to archive checksum %s",
                    archive_checksum,
                )
            else:
                self._grype_db_dir = latest_grype_db_dir
                self._grype_db_version = grype_db_version
                self._grype_db_session_maker = latest_grype_db_session_maker

                logger.info(
                    "Production grype_db updated to archive checksum %s",
=======
                self._staging_govulners_db_dir = latest_govulners_db_dir
                self._staging_govulners_db_version = govulners_db_version
                self._staging_govulners_db_session_maker = latest_govulners_db_session_maker

                logger.info(
                    "Staging govulners_db updated to archive checksum %s",
                    archive_checksum,
                )
            else:
                self._govulners_db_dir = latest_govulners_db_dir
                self._govulners_db_version = govulners_db_version
                self._govulners_db_session_maker = latest_govulners_db_session_maker

                logger.info(
                    "Production govulners_db updated to archive checksum %s",
>>>>>>> master
                    archive_checksum,
                )

            # Return the engine metadata as a data object
<<<<<<< HEAD
            return self.get_grype_db_engine_metadata(use_staging=use_staging)

    def unstage_grype_db(self) -> Optional[GrypeDBEngineMetadata]:
        """
        Unstages the staged grype_db. This method returns the production grype_db engine metadata, if a production
        grype_db has been set. Otherwise it returns None.
        """
        self._staging_grype_db_dir = None
        self._staging_grype_db_version = None
        self._staging_grype_db_session_maker = None

        # Return the existing, production engine metadata as a data object
        try:
            return self.get_grype_db_engine_metadata(use_staging=False)
        except ValueError as error:
            logger.warn(
                "Cannot return production grype_db engine metadata, as none has been set."
=======
            return self.get_govulners_db_engine_metadata(use_staging=use_staging)

    def unstage_govulners_db(self) -> Optional[GovulnersDBEngineMetadata]:
        """
        Unstages the staged govulners_db. This method returns the production govulners_db engine metadata, if a production
        govulners_db has been set. Otherwise it returns None.
        """
        self._staging_govulners_db_dir = None
        self._staging_govulners_db_version = None
        self._staging_govulners_db_session_maker = None

        # Return the existing, production engine metadata as a data object
        try:
            return self.get_govulners_db_engine_metadata(use_staging=False)
        except ValueError as error:
            logger.warn(
                "Cannot return production govulners_db engine metadata, as none has been set."
>>>>>>> master
            )
            return None

    def _get_metadata_file_contents(
        self, metadata_file_name, use_staging: bool = False
    ) -> json:
        """
<<<<<<< HEAD
        Return the json contents of one of the metadata files for the in-use version of grype db
=======
        Return the json contents of one of the metadata files for the in-use version of govulners db
>>>>>>> master
        """
        # Get the path to the latest metadata file, staging or prod
        if use_staging:
            latest_metadata_file = os.path.join(
<<<<<<< HEAD
                self._staging_grype_db_dir,
                self._staging_grype_db_version,
=======
                self._staging_govulners_db_dir,
                self._staging_govulners_db_version,
>>>>>>> master
                metadata_file_name,
            )
        else:
            latest_metadata_file = os.path.join(
<<<<<<< HEAD
                self._grype_db_dir, self._grype_db_version, metadata_file_name
=======
                self._govulners_db_dir, self._govulners_db_version, metadata_file_name
>>>>>>> master
            )

        # Ensure the file exists
        return self.read_file_to_json(latest_metadata_file)

<<<<<<< HEAD
    def get_grype_db_metadata(
        self, use_staging: bool = False
    ) -> Optional[GrypeDBMetadata]:
        """
        Return the contents of the current grype_db metadata file as a data object.
        This file contains metadata specific to grype about the current grype_db instance.
=======
    def get_govulners_db_metadata(
        self, use_staging: bool = False
    ) -> Optional[GovulnersDBMetadata]:
        """
        Return the contents of the current govulners_db metadata file as a data object.
        This file contains metadata specific to govulners about the current govulners_db instance.
>>>>>>> master
        This call can be parameterized to return either the production or staging metadata.
        """

        db_metadata = self._get_metadata_file_contents(
            self.METADATA_FILE_NAME, use_staging=use_staging
        )

        if db_metadata:
<<<<<<< HEAD
            return GrypeDBMetadata.to_object(db_metadata)
        else:
            return None

    def get_grype_db_engine_metadata(
        self, use_staging: bool = False
    ) -> Optional[GrypeDBEngineMetadata]:
        """
        Return the contents of the current grype_db engine metadata file as a data object.
        This file contains metadata specific to engine about the current grype_db instance.
=======
            return GovulnersDBMetadata.to_object(db_metadata)
        else:
            return None

    def get_govulners_db_engine_metadata(
        self, use_staging: bool = False
    ) -> Optional[GovulnersDBEngineMetadata]:
        """
        Return the contents of the current govulners_db engine metadata file as a data object.
        This file contains metadata specific to engine about the current govulners_db instance.
>>>>>>> master
        This call can be parameterized to return either the production or staging metadata.
        """

        engine_metadata = self._get_metadata_file_contents(
            self.ENGINE_METADATA_FILE_NAME, use_staging=use_staging
        )

        if engine_metadata:
<<<<<<< HEAD
            return GrypeDBEngineMetadata.to_object(engine_metadata)
=======
            return GovulnersDBEngineMetadata.to_object(engine_metadata)
>>>>>>> master
        else:
            return None

    def _get_env_variables(
<<<<<<< HEAD
        self, include_grype_db: bool = True, use_staging: bool = False
    ) -> Dict[str, str]:
        # Set grype env variables, optionally including the grype db location
        grype_env = self.GRYPE_BASE_ENV_VARS.copy()
        if include_grype_db:
            if use_staging:
                grype_env["GRYPE_DB_CACHE_DIR"] = self._staging_grype_db_dir
            else:
                grype_env["GRYPE_DB_CACHE_DIR"] = self._grype_db_dir

        env_variables = os.environ.copy()
        env_variables.update(grype_env)
        return env_variables

    def get_grype_version(self) -> json:
        """
        Return version information for grype
        """
        with self.read_lock_access():
            env_variables = self._get_env_variables(include_grype_db=False)

            logger.debug(
                "Getting grype version with command: %s", self.GRYPE_VERSION_COMMAND
=======
        self, include_govulners_db: bool = True, use_staging: bool = False
    ) -> Dict[str, str]:
        # Set govulners env variables, optionally including the govulners db location
        govulners_env = self.GOVULNERS_BASE_ENV_VARS.copy()
        if include_govulners_db:
            if use_staging:
                govulners_env["GOVULNERS_DB_CACHE_DIR"] = self._staging_govulners_db_dir
            else:
                govulners_env["GOVULNERS_DB_CACHE_DIR"] = self._govulners_db_dir

        env_variables = os.environ.copy()
        env_variables.update(govulners_env)
        return env_variables

    def get_govulners_version(self) -> json:
        """
        Return version information for govulners
        """
        with self.read_lock_access():
            env_variables = self._get_env_variables(include_govulners_db=False)

            logger.debug(
                "Getting govulners version with command: %s", self.GOVULNERS_VERSION_COMMAND
>>>>>>> master
            )

            stdout = None
            err = None
            try:
                stdout, _ = run_check(
<<<<<<< HEAD
                    shlex.split(self.GRYPE_VERSION_COMMAND), env=env_variables
=======
                    shlex.split(self.GOVULNERS_VERSION_COMMAND), env=env_variables
>>>>>>> master
                )
            except CommandException as exc:
                logger.error(
                    "Exception running command: %s, stderr: %s",
<<<<<<< HEAD
                    self.GRYPE_VERSION_COMMAND,
=======
                    self.GOVULNERS_VERSION_COMMAND,
>>>>>>> master
                    exc.stderr,
                )
                raise exc

            # Return the output as json
            return json.loads(stdout)

<<<<<<< HEAD
    def get_vulnerabilities_for_sbom(self, grype_sbom: str) -> json:
        """
        Use grype to scan the provided sbom for vulnerabilites.
        """
        # Get the read lock
        with self.read_lock_access():
            # Get env variables to run the grype scan with
            env_variables = self._get_env_variables()

            # Format and run the command. Grype supports piping in an sbom string
            cmd = "{}".format(self.GRYPE_SUB_COMMAND)

            logger.spew(
                "Running grype with command: {} | {}".format(
                    grype_sbom, self.GRYPE_SUB_COMMAND
=======
    def get_vulnerabilities_for_sbom(self, govulners_sbom: str) -> json:
        """
        Use govulners to scan the provided sbom for vulnerabilites.
        """
        # Get the read lock
        with self.read_lock_access():
            # Get env variables to run the govulners scan with
            env_variables = self._get_env_variables()

            # Format and run the command. Govulners supports piping in an sbom string
            cmd = "{}".format(self.GOVULNERS_SUB_COMMAND)

            logger.spew(
                "Running govulners with command: {} | {}".format(
                    govulners_sbom, self.GOVULNERS_SUB_COMMAND
>>>>>>> master
                )
            )

            try:
                stdout, _ = run_check(
                    shlex.split(cmd),
<<<<<<< HEAD
                    input_data=grype_sbom,
=======
                    input_data=govulners_sbom,
>>>>>>> master
                    log_level="spew",
                    env=env_variables,
                )
            except CommandException as exc:
                logger.error(
                    "Exception running command: %s, stderr: %s",
                    cmd,
                    exc.stderr,
                )
                raise exc

            # Return the output as json
            return json.loads(stdout)

<<<<<<< HEAD
    def get_vulnerabilities_for_sbom_file(self, grype_sbom_file: str) -> json:
        """
        Use grype to scan the provided sbom for vulnerabilites.
        """
        # Get the read lock
        with self.read_lock_access():
            # Get env variables to run the grype scan with
            env_variables = self._get_env_variables()

            # Format and run the command
            cmd = "{grype_sub_command} sbom:{sbom}".format(
                grype_sub_command=self.GRYPE_SUB_COMMAND, sbom=grype_sbom_file
            )

            logger.debug("Running grype with command: %s", cmd)
=======
    def get_vulnerabilities_for_sbom_file(self, govulners_sbom_file: str) -> json:
        """
        Use govulners to scan the provided sbom for vulnerabilites.
        """
        # Get the read lock
        with self.read_lock_access():
            # Get env variables to run the govulners scan with
            env_variables = self._get_env_variables()

            # Format and run the command
            cmd = "{govulners_sub_command} sbom:{sbom}".format(
                govulners_sub_command=self.GOVULNERS_SUB_COMMAND, sbom=govulners_sbom_file
            )

            logger.debug("Running govulners with command: %s", cmd)
>>>>>>> master

            stdout = None
            err = None
            try:
                stdout, _ = run_check(
                    shlex.split(cmd), log_level="spew", env=env_variables
                )
            except CommandException as exc:
                logger.error(
                    "Exception running command: %s, stderr: %s",
                    cmd,
                    exc.stderr,
                )
                raise exc

            # Return the output as json
            return json.loads(stdout)

    def query_vulnerability_metadata(
        self, vuln_ids: List[str], namespaces: List[str]
<<<<<<< HEAD
    ) -> Iterable[GrypeVulnerabilityMetadata]:
        """
        Provided a list of vulnerability ids and namespaces, returns a list of matching GrypeVulnerabilityMetadata records
=======
    ) -> Iterable[GovulnersVulnerabilityMetadata]:
        """
        Provided a list of vulnerability ids and namespaces, returns a list of matching GovulnersVulnerabilityMetadata records
>>>>>>> master
        """

        if not vuln_ids:
            logger.debug("No vulnerabilities provided for query")
            return []

        with self.read_lock_access():
            logger.debug(
<<<<<<< HEAD
                "Querying grype_db for GrypeVulenrabilityMetadata records matching vuln_ids: %s, namespace: %s",
=======
                "Querying govulners_db for GovulnersVulenrabilityMetadata records matching vuln_ids: %s, namespace: %s",
>>>>>>> master
                vuln_ids,
                namespaces,
            )

<<<<<<< HEAD
            with self.grype_session_scope() as session:
                query = session.query(GrypeVulnerabilityMetadata).filter(
                    GrypeVulnerabilityMetadata.id.in_(vuln_ids)
=======
            with self.govulners_session_scope() as session:
                query = session.query(GovulnersVulnerabilityMetadata).filter(
                    GovulnersVulnerabilityMetadata.id.in_(vuln_ids)
>>>>>>> master
                )

                if namespaces:
                    query = query.filter(
<<<<<<< HEAD
                        GrypeVulnerabilityMetadata.namespace.in_(namespaces)
=======
                        GovulnersVulnerabilityMetadata.namespace.in_(namespaces)
>>>>>>> master
                    )

                return query.all()

    def query_vulnerabilities(
        self,
        vuln_id=None,
        affected_package=None,
        affected_package_version=None,
        namespace=None,
    ):
        """
<<<<<<< HEAD
        Query the grype db for vulnerabilites. affected_package_version is unused, but is left in place for now to match the
=======
        Query the govulners db for vulnerabilites. affected_package_version is unused, but is left in place for now to match the
>>>>>>> master
        header of the existing function this is meant to replace.
        """
        # Get and release read locks
        with self.read_lock_access():
            if type(vuln_id) == str:
                vuln_id = [vuln_id]

            if type(namespace) == str:
                namespace = [namespace]

            logger.debug(
<<<<<<< HEAD
                "Querying grype_db for vuln_id: %s, namespace: %s, affected_package: %s",
=======
                "Querying govulners_db for vuln_id: %s, namespace: %s, affected_package: %s",
>>>>>>> master
                vuln_id,
                namespace,
                affected_package,
            )

<<<<<<< HEAD
            with self.grype_session_scope() as session:
                # GrypeVulnerabilityMetadata contains info for the vulnerability. GrypeVulnerability contains info for the affected/fixed package
                # A vulnerability can impact 0 or more packages i.e. a GrypeVulnerabilityMetadata row can be associated with 0 or more GrypeVulnerability rows
                # Since the lookup is for vulnerability information, the query should left outer join GrypeVulnerabilityMetadata with GrypeVulnerability
                query = session.query(
                    GrypeVulnerability, GrypeVulnerabilityMetadata
                ).outerjoin(
                    GrypeVulnerability,
                    and_(
                        GrypeVulnerability.id == GrypeVulnerabilityMetadata.id,
                        GrypeVulnerability.namespace
                        == GrypeVulnerabilityMetadata.namespace,
=======
            with self.govulners_session_scope() as session:
                # GovulnersVulnerabilityMetadata contains info for the vulnerability. GovulnersVulnerability contains info for the affected/fixed package
                # A vulnerability can impact 0 or more packages i.e. a GovulnersVulnerabilityMetadata row can be associated with 0 or more GovulnersVulnerability rows
                # Since the lookup is for vulnerability information, the query should left outer join GovulnersVulnerabilityMetadata with GovulnersVulnerability
                query = session.query(
                    GovulnersVulnerability, GovulnersVulnerabilityMetadata
                ).outerjoin(
                    GovulnersVulnerability,
                    and_(
                        GovulnersVulnerability.id == GovulnersVulnerabilityMetadata.id,
                        GovulnersVulnerability.namespace
                        == GovulnersVulnerabilityMetadata.namespace,
>>>>>>> master
                    ),
                )

                if vuln_id is not None:
<<<<<<< HEAD
                    query = query.filter(GrypeVulnerability.id.in_(vuln_id))
                if namespace is not None:
                    query = query.filter(GrypeVulnerability.namespace.in_(namespace))
                if affected_package is not None:
                    query = query.filter(
                        GrypeVulnerability.package_name == affected_package
                    )

                logger.debug("grype_db sql query for vulnerabilities lookup: %s", query)
=======
                    query = query.filter(GovulnersVulnerability.id.in_(vuln_id))
                if namespace is not None:
                    query = query.filter(GovulnersVulnerability.namespace.in_(namespace))
                if affected_package is not None:
                    query = query.filter(
                        GovulnersVulnerability.package_name == affected_package
                    )

                logger.debug("govulners_db sql query for vulnerabilities lookup: %s", query)
>>>>>>> master

                return query.all()

    def query_record_source_counts(self, use_staging: bool = False):
        """
        Query the current feed group counts for all current vulnerabilities.
        """
        # Get and release read locks
        with self.read_lock_access():
<<<<<<< HEAD
            logger.debug("Querying grype_db for feed group counts")

            # Get the counts for each record source
            with self.grype_session_scope(use_staging) as session:
                results = (
                    session.query(
                        GrypeVulnerabilityMetadata.namespace,
                        func.count(GrypeVulnerabilityMetadata.namespace).label("count"),
                    )
                    .group_by(GrypeVulnerabilityMetadata.namespace)
=======
            logger.debug("Querying govulners_db for feed group counts")

            # Get the counts for each record source
            with self.govulners_session_scope(use_staging) as session:
                results = (
                    session.query(
                        GovulnersVulnerabilityMetadata.namespace,
                        func.count(GovulnersVulnerabilityMetadata.namespace).label("count"),
                    )
                    .group_by(GovulnersVulnerabilityMetadata.namespace)
>>>>>>> master
                    .all()
                )

                # Get the timestamp from the current metadata file
                last_synced = None
<<<<<<< HEAD
                if db_metadata := self.get_grype_db_metadata(use_staging):
=======
                if db_metadata := self.get_govulners_db_metadata(use_staging):
>>>>>>> master
                    last_synced = db_metadata.built

                # Transform the results along with the last_synced timestamp for each result
                output = []
                for group, count in results:
                    record_source = RecordSource(
                        count=count,
                        feed=VULNERABILITIES,
                        group=group,
                        last_synced=last_synced,
                    )
                    output.append(record_source)

                # Return the results
                return output
