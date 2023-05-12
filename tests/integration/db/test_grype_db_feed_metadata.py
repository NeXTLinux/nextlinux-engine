from datetime import datetime

import pytest

<<<<<<< HEAD
from nextlinux_engine.db import GrypeDBFeedMetadata, session_scope
from nextlinux_engine.db.db_grype_db_feed_metadata import (
    NoActiveGrypeDB,
    get_most_recent_active_grypedb,
=======
from nextlinux_engine.db import GovulnersDBFeedMetadata, session_scope
from nextlinux_engine.db.db_govulners_db_feed_metadata import (
    NoActiveGovulnersDB,
    get_most_recent_active_govulnersdb,
>>>>>>> master
)

meta_objs = [
    GovulnersDBFeedMetadata(
        archive_checksum="first_meta",
        schema_version="2",
        object_url="1234",
        active=True,
        built_at=datetime.utcnow(),
    ),
    GovulnersDBFeedMetadata(
        archive_checksum="second_meta",
        schema_version="2",
        object_url="1234",
        active=True,
        built_at=datetime.utcnow(),
    ),
]


<<<<<<< HEAD
def test_get_most_recent_active_grypedb(nextlinux_db):
=======
def test_get_most_recent_active_govulnersdb(nextlinux_db):
>>>>>>> master
    with session_scope() as session:
        session.add(meta_objs[0])
        session.commit()

        govulners_db = get_most_recent_active_govulnersdb(session)
        assert isinstance(govulners_db, GovulnersDBFeedMetadata) is True
        assert govulners_db.archive_checksum == "first_meta"


<<<<<<< HEAD
def test_get_most_recent_active_grypedb_no_active_Db(nextlinux_db):
=======
def test_get_most_recent_active_govulnersdb_no_active_Db(nextlinux_db):
>>>>>>> master
    with session_scope() as session:
        with pytest.raises(NoActiveGovulnersDB):
            get_most_recent_active_govulnersdb(session)


<<<<<<< HEAD
def test_get_most_recent_active_grypedb_multiple_active(nextlinux_db):
=======
def test_get_most_recent_active_govulnersdb_multiple_active(nextlinux_db):
>>>>>>> master
    with session_scope() as session:
        for meta in meta_objs:
            session.add(meta)
        session.commit()

        govulners_db = get_most_recent_active_govulnersdb(session)
        assert isinstance(govulners_db, GovulnersDBFeedMetadata) is True
        assert govulners_db.archive_checksum == "second_meta"
