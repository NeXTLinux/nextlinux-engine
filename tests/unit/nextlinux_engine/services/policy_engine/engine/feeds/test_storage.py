import os

import pytest

from nextlinux_engine.services.policy_engine.engine.feeds.storage import (
    ChecksumMismatchError,
    GovulnersDBFile,
    GovulnersDBStorage,
)

test_data = b"test"
test_data_checksum = (
    "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")
malformed_data = b"test123"


class TestStorage:

    def test_integrity_verification(self):
        """
        Test class function that verifies checksum of data
        """
        GovulnersDBFile.verify_integrity(test_data, test_data_checksum)

        with pytest.raises(ChecksumMismatchError):
            GovulnersDBFile.verify_integrity(malformed_data,
                                             test_data_checksum)

    def test_directory_creation_and_cleanup(self):
        """
        Tests that the temp directory is created by context manager and then is deleted once exited
        """
        with GovulnersDBStorage() as grypedb_file:
            directory_path = grypedb_file.root_directory
            assert os.path.exists(directory_path) is True

        assert os.path.exists(directory_path) is False

    def test_file_creation_and_cleanup(self):
        """
        Tests that file created exists in context but is deleted once exited
        """
        with GovulnersDBStorage() as grypedb_file:
            with grypedb_file.create_file(test_data_checksum) as f:
                f.write(test_data)
            file_path = grypedb_file._file_path
            assert os.path.exists(file_path) is True

        assert os.path.exists(file_path) is False

    def test_verify_integrity_on_file_creation(self):
        """
        Integrity is also verified on file creation so tests that error is thrown when it does not match
        """
        with pytest.raises(ChecksumMismatchError):
            with GovulnersDBStorage() as grypedb_file:
                with grypedb_file.create_file(test_data_checksum) as f:
                    f.write(malformed_data)

    def test_file_data(self):
        with GovulnersDBStorage() as grypedb_file:
            with grypedb_file.create_file(test_data_checksum) as f:
                f.write(test_data)

            with open(grypedb_file._file_path, "rb") as f:
                assert test_data == f.read()
