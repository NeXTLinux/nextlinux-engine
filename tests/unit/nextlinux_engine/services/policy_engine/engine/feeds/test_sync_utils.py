from typing import Dict, List, Type

import pytest

from nextlinux_engine.common.models.schemas import (
    FeedAPIGroupRecord,
    FeedAPIRecord,
    GovulnersDBListing,
)
from nextlinux_engine.db import FeedGroupMetadata, FeedMetadata
from nextlinux_engine.db.entities.common import nextlinux_now_datetime
from nextlinux_engine.services.policy_engine.engine.feeds import FeedList
from nextlinux_engine.services.policy_engine.engine.feeds.client import (
    FeedServiceClient,
    GovulnersDBServiceClient,
    IFeedSource,
)
from nextlinux_engine.services.policy_engine.engine.feeds.config import SyncConfig
from nextlinux_engine.services.policy_engine.engine.feeds.feeds import (
<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/feeds/test_sync_utils.py
    GrypeDBFeed,
    VulnerabilityFeed,
)
from nextlinux_engine.services.policy_engine.engine.feeds.sync_utils import (
    GrypeDBSyncUtilProvider,
=======
    GovulnersDBFeed,
    VulnerabilityFeed,
)
from nextlinux_engine.services.policy_engine.engine.feeds.sync_utils import (
    GovulnersDBSyncUtilProvider,
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/feeds/test_sync_utils.py
    LegacySyncUtilProvider,
    SyncUtilProvider,
)


class TestSyncUtilProvider:
    @pytest.mark.parametrize(
        "sync_util_provider, sync_configs, expected_to_sync_after_filtering",
        [
            (
                LegacySyncUtilProvider,
                {"packages": SyncConfig(url="www.nextlinux.com", enabled=True)},
                ["packages"],
            ),
            (
                LegacySyncUtilProvider,
                {
                    "nvdv2": SyncConfig(url="www.nextlinux.com", enabled=True),
                    "vulnerabilities": SyncConfig(url="www.nextlinux.com", enabled=True),
                },
                ["nvdv2", "vulnerabilities"],
            ),
            (
<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/feeds/test_sync_utils.py
                GrypeDBSyncUtilProvider,
                {"grypedb": SyncConfig(url="www.nextlinux.com", enabled=True)},
                ["grypedb"],
=======
                GovulnersDBSyncUtilProvider,
                {"govulnersdb": SyncConfig(url="www.nextlinux.com", enabled=True)},
                ["govulnersdb"],
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/feeds/test_sync_utils.py
            ),
            (
                GovulnersDBSyncUtilProvider,
                {
<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/feeds/test_sync_utils.py
                    "grypedb": SyncConfig(url="www.nextlinux.com", enabled=True),
=======
                    "govulnersdb": SyncConfig(url="www.nextlinux.com", enabled=True),
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/feeds/test_sync_utils.py
                    "packages": SyncConfig(url="www.nextlinux.com", enabled=True),
                },
                ["govulnersdb"],
            ),
        ],
    )
    def test_get_filtered_sync_configs(
        self,
        sync_util_provider: Type[SyncUtilProvider],
        sync_configs: Dict[str, SyncConfig],
        expected_to_sync_after_filtering: List[str],
    ):
        """
        This is a bit confusing and probably should be changed, which is why i've written a test for it.
        There are two SyncUtilProviders.
        The LegacySyncUtilProvider works for all feeds that follow the legacy format.
        The GovulnersDBSyncUtilProvider works for the GovulnersDB feed format.
        However, the VulnerabilitiesProvider has two implementations.
        The LegacyProvider contains all vulnerability logic that changes when the provider is set to "legacy"
        The GovulnersProvider contains all vulnerability logic that changes when the provider is set to "govulners"
        As such, the GovulnersProvider actually returns both "packages" and "govulnersdb" SyncConfigs,
        while "packages" is actually a Legacy style feed.
        Meanwhile, the "packages" feed can only be synced by the LegacySyncUtilProvider.
        The solution is likely to wrap the entire sync method with the SyncUtilProvider, that way LegacySyncUtilProvider
        can just do legacy feeds, while GovulnersDBSyncUtilProvider will first do "govulnersdb" feed with the govulners logic
        and then do "packages" feed with the legacy logic.
        """
        filtered_configs = sync_util_provider._get_filtered_sync_configs(sync_configs)
        assert set(filtered_configs) == set(expected_to_sync_after_filtering)

    @pytest.mark.parametrize(
        "sync_util_provider, sync_configs, expected_client_class",
        [
            (
                LegacySyncUtilProvider,
                {"vulnerabilities": SyncConfig(url="www.nextlinux.com", enabled=True)},
                FeedServiceClient,
            ),
            (
<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/feeds/test_sync_utils.py
                GrypeDBSyncUtilProvider,
                {"grypedb": SyncConfig(url="www.nextlinux.com", enabled=True)},
                GrypeDBServiceClient,
=======
                GovulnersDBSyncUtilProvider,
                {"govulnersdb": SyncConfig(url="www.nextlinux.com", enabled=True)},
                GovulnersDBServiceClient,
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/feeds/test_sync_utils.py
            ),
        ],
    )
    def test_get_client(
        self,
        sync_util_provider: Type[SyncUtilProvider],
        sync_configs: Dict[str, SyncConfig],
        expected_client_class: Type[IFeedSource],
    ):
        client = sync_util_provider(sync_configs).get_client()
        assert isinstance(client, expected_client_class)

    @pytest.mark.parametrize(
        "metadata, expected_number_groups, expected_feed_group_metadata",
        [
            (
                FeedMetadata(name="govulnersdb", enabled=True),
                1,
                FeedGroupMetadata(
                    name="govulnersdb:vulnerabilities", feed_name="govulnersdb", enabled=True
                ),
            ),
            (FeedMetadata(name="govulnersdb", enabled=False), 0, None),
        ],
    )
    def test_get_groups_to_download_govulners(
        self,
        metadata: FeedMetadata,
        expected_number_groups: int,
        expected_feed_group_metadata: FeedMetadata,
    ):
        source_feeds = {
            "govulnersdb": {
                "meta": FeedList(
                    feeds=[
                        FeedAPIRecord(
                            name="govulnersdb",
                            description="govulnersdb feed",
                            access_tier="0",
                        )
                    ]
                ),
                "groups": [
                    FeedAPIGroupRecord(
                        name="govulnersdb:vulnerabilities",
                        description="govulnersdb:vulnerabilities group",
                        access_tier="0",
<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/feeds/test_sync_utils.py
                        grype_listing=GrypeDBListing(
=======
                        govulners_listing=GovulnersDBListing(
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/feeds/test_sync_utils.py
                            built=nextlinux_now_datetime(),
                            version="2",
                            url="www.nextlinux.com",
                            checksum="sha256:xxx",
                        ),
                    )
                ],
            }
        }
<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/feeds/test_sync_utils.py
        feeds_to_sync = [GrypeDBFeed(metadata=metadata)]
        sync_config = {"grypedb": SyncConfig(enabled=True, url="www.nextlinux.com")}
        groups_to_download = GrypeDBSyncUtilProvider(
=======
        feeds_to_sync = [GovulnersDBFeed(metadata=metadata)]
        sync_config = {"govulnersdb": SyncConfig(enabled=True, url="www.nextlinux.com")}
        groups_to_download = GovulnersDBSyncUtilProvider(
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/feeds/test_sync_utils.py
            sync_config
        ).get_groups_to_download(source_feeds, feeds_to_sync, "0")
        assert len(groups_to_download) == expected_number_groups
        if expected_number_groups > 0:
            group = groups_to_download[0]
            assert group.enabled == expected_feed_group_metadata.enabled
            assert group.feed_name == expected_feed_group_metadata.feed_name
            assert group.name == expected_feed_group_metadata.name

    def test_get_groups_to_download_legacy(self):
        feed_group_metadata = [
            FeedGroupMetadata(name="vulnerabilities:alpine:3.10", enabled=True),
            FeedGroupMetadata(name="vulnerabilities:alpine:3.11", enabled=True),
        ]
        feeds_to_sync = [
            VulnerabilityFeed(
                metadata=FeedMetadata(
                    name="vulnerabilities",
                    enabled=True,
                    groups=feed_group_metadata,
                )
            )
        ]
        sync_config = {
            "vulnerabilities": SyncConfig(enabled=True, url="www.nextlinux.com")
        }
        groups_to_download = LegacySyncUtilProvider(sync_config).get_groups_to_download(
            {}, feeds_to_sync, "0"
        )
        assert groups_to_download == feed_group_metadata
