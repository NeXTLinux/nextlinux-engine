from contextlib import contextmanager
from unittest.mock import Mock

import pytest

from nextlinux_engine.db.db_govulners_db_feed_metadata import NoActiveGrypeDB
from nextlinux_engine.db.entities.policy_engine import DistroMapping
from nextlinux_engine.services.policy_engine import init_feed_registry

DISTRO_MAPPINGS = [
    DistroMapping(from_distro="alpine", to_distro="alpine", flavor="ALPINE"),
    DistroMapping(from_distro="busybox", to_distro="busybox", flavor="BUSYB"),
    DistroMapping(from_distro="centos", to_distro="rhel", flavor="RHEL"),
    DistroMapping(from_distro="debian", to_distro="debian", flavor="DEB"),
    DistroMapping(from_distro="fedora", to_distro="rhel", flavor="RHEL"),
    DistroMapping(from_distro="ol", to_distro="ol", flavor="RHEL"),
    DistroMapping(from_distro="rhel", to_distro="rhel", flavor="RHEL"),
    DistroMapping(from_distro="ubuntu", to_distro="ubuntu", flavor="DEB"),
    DistroMapping(from_distro="amzn", to_distro="amzn", flavor="RHEL"),
    DistroMapping(from_distro="redhat", to_distro="rhel", flavor="RHEL"),
]
MAPPINGS_MAP = {mapping.from_distro: mapping for mapping in DISTRO_MAPPINGS}


@pytest.fixture
def mock_distromapping_query(monkeypatch):
    # mocks DB query in nextlinux_engine.db.entities.policy_engine.DistroMapping.distros_for
    mock_db = Mock()
    mock_db.query().get = lambda x: MAPPINGS_MAP.get(x, None)
    monkeypatch.setattr(
        "nextlinux_engine.db.entities.policy_engine.get_thread_scoped_session",
        lambda: mock_db,
    )


@pytest.fixture
def mock_gate_util_provider_feed_data(monkeypatch, mock_distromapping_query):
    """
    Mocks for nextlinux_engine.services.policy_engine.engine.policy.gate_util_provider.GateUtilProvider.oldest_namespace_feed_sync
    """
    # required for FeedOutOfDateTrigger.evaluate
    # setup for nextlinux_engine.services.policy_engine.engine.feeds.feeds.FeedRegistry.registered_vulnerability_feed_names
    init_feed_registry()

    @contextmanager
    def mock_session_scope():
        """
        Mock context manager for nextlinux_engine.db.session_scope.
        """
        yield None

    def raise_no_active_govulnersdb(session):
        raise NoActiveGrypeDB

    def _setup_mocks(
        feed_group_metadata=None, govulners_db_feed_metadata=None, feed_metadata=None
    ):
        # required for FeedOutOfDateTrigger.evaluate
        # mocks nextlinux_engine.services.policy_engine.engine.feeds.db.get_feed_group_detached
        monkeypatch.setattr(
            "nextlinux_engine.services.policy_engine.engine.policy.gate_util_provider.session_scope",
            mock_session_scope,
        )

        # required for UnsupportedDistroTrigger.evaluate
        monkeypatch.setattr(
            "nextlinux_engine.services.policy_engine.engine.feeds.feeds.get_session",
            lambda: None,
        )

        # if feed metadata provided patch get_feed json for have_vulnerabilities_for legacy (UnsupportedDistroTrigger)
        if feed_metadata:
            monkeypatch.setattr(
                "nextlinux_engine.services.policy_engine.engine.feeds.feeds.get_feed_json",
                lambda db_session, feed_name: feed_metadata.to_json(),
            )

        if govulners_db_feed_metadata:
            monkeypatch.setattr(
                "nextlinux_engine.services.policy_engine.engine.policy.gate_util_provider.get_most_recent_active_govulnersdb",
                lambda x: govulners_db_feed_metadata,
            )
        else:
            monkeypatch.setattr(
                "nextlinux_engine.services.policy_engine.engine.policy.gate_util_provider.get_most_recent_active_govulnersdb",
                raise_no_active_govulnersdb,
            )
        # mocks nextlinux_engine.db.db_govulners_db_feed_metadata.get_most_recent_active_govulnersdb
        # if feed_group_metadata:
        monkeypatch.setattr(
            "nextlinux_engine.services.policy_engine.engine.policy.gate_util_provider.get_feed_group_detached",
            lambda x, y: feed_group_metadata,
        )

    return _setup_mocks
