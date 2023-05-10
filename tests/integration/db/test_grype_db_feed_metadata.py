from datetime import datetime

import pytest

from nextlinux_engine.db import GovulnersDBFeedMetadata, session_scope
from nextlinux_engine.db.db_govulners_db_feed_metadata import (
    NoActiveGovulnersDB,
    get_most_recent_active_govulnersdb,
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


def test_get_most_recent_active_govulnersdb(nextlinux_db):
    with session_scope() as session:
        session.add(meta_objs[0])
        session.commit()

        govulners_db = get_most_recent_active_govulnersdb(session)
        assert isinstance(govulners_db, GovulnersDBFeedMetadata) is True
        assert govulners_db.archive_checksum == "first_meta"


def test_get_most_recent_active_govulnersdb_no_active_Db(nextlinux_db):
    with session_scope() as session:
        with pytest.raises(NoActiveGovulnersDB):
            get_most_recent_active_govulnersdb(session)


def test_get_most_recent_active_govulnersdb_multiple_active(nextlinux_db):
    with session_scope() as session:
        for meta in meta_objs:
            session.add(meta)
        session.commit()

        govulners_db = get_most_recent_active_govulnersdb(session)
        assert isinstance(govulners_db, GovulnersDBFeedMetadata) is True
        assert govulners_db.archive_checksum == "second_meta"
