<<<<<<< HEAD
from nextlinux_engine.db import GrypeDBFeedMetadata
from nextlinux_engine.subsys import logger


class NoActiveGrypeDB(Exception):
    def __init__(self):
        super().__init__("No active grypedb available")


def get_most_recent_active_grypedb(session) -> GrypeDBFeedMetadata:
    """
    Queries active GrypeDBFeedMetadata order by created at desc
    If no active grypedb, raises NoActiveGrypeDB
    """
    active_db = (
        session.query(GrypeDBFeedMetadata)
        .filter(GrypeDBFeedMetadata.active.is_(True))
        .order_by(GrypeDBFeedMetadata.created_at.desc())
=======
from nextlinux_engine.db import GovulnersDBFeedMetadata
from nextlinux_engine.subsys import logger


class NoActiveGovulnersDB(Exception):
    def __init__(self):
        super().__init__("No active govulnersdb available")


def get_most_recent_active_govulnersdb(session) -> GovulnersDBFeedMetadata:
    """
    Queries active GovulnersDBFeedMetadata order by created at desc
    If no active govulnersdb, raises NoActiveGovulnersDB
    """
    active_db = (
        session.query(GovulnersDBFeedMetadata)
        .filter(GovulnersDBFeedMetadata.active.is_(True))
        .order_by(GovulnersDBFeedMetadata.created_at.desc())
>>>>>>> master
        .limit(1)
        .all()
    )

    if not active_db:
<<<<<<< HEAD
        logger.error("No active grypedb found")
        raise NoActiveGrypeDB
=======
        logger.error("No active govulnersdb found")
        raise NoActiveGovulnersDB
>>>>>>> master
    else:
        return active_db[0]
