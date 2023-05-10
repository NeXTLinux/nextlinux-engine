import datetime
from typing import Optional, Type
from unittest.mock import Mock

import pytest

from nextlinux_engine.db.entities.policy_engine import (
    DistroNamespace,
    FeedGroupMetadata,
    GrypeDBFeedMetadata,
)
from nextlinux_engine.services.policy_engine.engine.policy.gate_util_provider import (
    GateUtilProvider,
    GrypeGateUtilProvider,
    LegacyGateUtilProvider,
)

govulners_db_for_unsupported_distro = GrypeDBFeedMetadata(
    groups=[
        {"name": "ubuntu:20.04", "record_count": 4909},
        {"name": "amzn:2", "record_count": 0},
        {"name": "alpine:3.10", "record_count": 200},
        {"name": "debian:10", "record_count": 500},
        {"name": "github:python", "record_count": 800},
    ]
)


class TestGateUtilProvider:
    sync_time = datetime.datetime.utcnow()

    @pytest.mark.parametrize(
        "gate_util_provider, feed_group_metadata, govulners_db_feed_metadata, expected_oldest_update",
        [
            # Case, legacy provider, feed group exists
            (
                LegacyGateUtilProvider,
                FeedGroupMetadata(
                    last_sync=sync_time,
                    name="test-feed-out-of-date",
                ),
                None,
                sync_time,
            ),
            # Case, legacy provider, feed group does not exist
            (
                LegacyGateUtilProvider,
                None,
                None,
                None,
            ),
            # Case, govulners provider, active govulners DB exists
            (
                GrypeGateUtilProvider,
                None,
                GrypeDBFeedMetadata(built_at=sync_time),
                sync_time,
            ),
            # Case, govulners provider, active govulners DB does not exist
            (
                GrypeGateUtilProvider,
                None,
                None,
                None,
            ),
        ],
    )
    def test_oldest_namespace_feed_sync(
        self,
        gate_util_provider: Type[GateUtilProvider],
        feed_group_metadata: Optional[FeedGroupMetadata],
        govulners_db_feed_metadata: Optional[GrypeDBFeedMetadata],
        expected_oldest_update: Optional[datetime.datetime],
        mock_distromapping_query,
        mock_gate_util_provider_feed_data,
    ):
        ns = DistroNamespace(name="DEB", version="10", like_distro=None)
        ns.like_namespace_names = ["debian:10"]

        mock_gate_util_provider_feed_data(
            feed_group_metadata=feed_group_metadata,
            govulners_db_feed_metadata=govulners_db_feed_metadata,
        )

        provider = gate_util_provider()
        oldest_update = provider.oldest_namespace_feed_sync(ns)

        assert oldest_update == expected_oldest_update

    @pytest.mark.parametrize(
        "govulnersdb, distro, version, expected",
        [
            (govulners_db_for_unsupported_distro, "amzn", "2", False),
            (govulners_db_for_unsupported_distro, "alpine", "3.10", True),
            (govulners_db_for_unsupported_distro, "debian", "10", True),
            (govulners_db_for_unsupported_distro, "github", "python", True),
            (govulners_db_for_unsupported_distro, "ubuntu", "17.04", False),
            (None, "alpine", "3.10", False),  # This one tests no active govulnersdb
            (GrypeDBFeedMetadata(groups=None), "alpine", "3.10", False),
        ],
    )
    def test_have_vulnerabilities_for_govulners_provider(
        self,
        govulnersdb,
        distro: str,
        version: str,
        expected: bool,
        mock_gate_util_provider_feed_data,
    ):
        # Setup
        distro_namespace = Mock()
        base_distro_name = distro + ":" + version
        distro_namespace.like_namespace_names = [
            f"{base_distro_name}.0",
            f"{base_distro_name}.1",
            f"{base_distro_name}.2",
            base_distro_name,
        ]
        provider = GrypeGateUtilProvider()

        mock_gate_util_provider_feed_data(govulners_db_feed_metadata=govulnersdb)

        # Method under test
        result = provider.have_vulnerabilities_for(distro_namespace)

        # Assert expected result
        assert result is expected
