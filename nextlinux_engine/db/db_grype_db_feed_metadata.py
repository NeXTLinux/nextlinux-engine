from nextlinux_engine.db import GrypeDBFeedMetadata
from nextlinux_engine.subsys import logger


class NoActiveGrypeDB(Exception):
    def __init__(self):
        super().__init__("No active govulnersdb available")


def get_most_recent_active_govulnersdb(session) -> GrypeDBFeedMetadata:
    """
    Queries active GrypeDBFeedMetadata order by created at desc
    If no active govulnersdb, raises NoActiveGrypeDB
    """
    active_db = (
        session.query(GrypeDBFeedMetadata)
        .filter(GrypeDBFeedMetadata.active.is_(True))
        .order_by(GrypeDBFeedMetadata.created_at.desc())
        .limit(1)
        .all()
    )

    if not active_db:
        logger.error("No active govulnersdb found")
        raise NoActiveGrypeDB
    else:
        return active_db[0]
