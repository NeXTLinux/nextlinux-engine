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
    GovulnersDBFeed,
    VulnerabilityFeed,
)
from nextlinux_engine.services.policy_engine.engine.feeds.sync_utils import (
    GovulnersDBSyncUtilProvider,
    LegacySyncUtilProvider,
    SyncUtilProvider,
)


class TestSyncUtilProvider:

    @pytest.mark.parametrize(
        "sync_util_provider, sync_configs, expected_to_sync_after_filtering",
        [
            (
                LegacySyncUtilProvider,
                {
                    "packages":
                    SyncConfig(url="www.next-linux.systems", enabled=True)
                },
                ["packages"],
            ),
            (
                LegacySyncUtilProvider,
                {
                    "nvdv2":
                    SyncConfig(url="www.next-linux.systems", enabled=True),
                    "vulnerabilities":
                    SyncConfig(url="www.next-linux.systems", enabled=True),
                },
                ["nvdv2", "vulnerabilities"],
            ),
            (
                GovulnersDBSyncUtilProvider,
                {
                    "grypedb":
                    SyncConfig(url="www.next-linux.systems", enabled=True)
                },
                ["grypedb"],
            ),
            (
                GovulnersDBSyncUtilProvider,
                {
                    "grypedb":
                    SyncConfig(url="www.next-linux.systems", enabled=True),
                    "packages":
                    SyncConfig(url="www.next-linux.systems", enabled=True),
                },
                ["grypedb"],
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
        The GovulnersProvider contains all vulnerability logic that changes when the provider is set to "grype"
        As such, the GovulnersProvider actually returns both "packages" and "grypedb" SyncConfigs,
        while "packages" is actually a Legacy style feed.
        Meanwhile, the "packages" feed can only be synced by the LegacySyncUtilProvider.
        The solution is likely to wrap the entire sync method with the SyncUtilProvider, that way LegacySyncUtilProvider
        can just do legacy feeds, while GovulnersDBSyncUtilProvider will first do "grypedb" feed with the grype logic
        and then do "packages" feed with the legacy logic.
        """
        filtered_configs = sync_util_provider._get_filtered_sync_configs(
            sync_configs)
        assert set(filtered_configs) == set(expected_to_sync_after_filtering)

    @pytest.mark.parametrize(
        "sync_util_provider, sync_configs, expected_client_class",
        [
            (
                LegacySyncUtilProvider,
                {
                    "vulnerabilities":
                    SyncConfig(url="www.next-linux.systems", enabled=True)
                },
                FeedServiceClient,
            ),
            (
                GovulnersDBSyncUtilProvider,
                {
                    "grypedb":
                    SyncConfig(url="www.next-linux.systems", enabled=True)
                },
                GovulnersDBServiceClient,
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
                FeedMetadata(name="grypedb", enabled=True),
                1,
                FeedGroupMetadata(name="grypedb:vulnerabilities",
                                  feed_name="grypedb",
                                  enabled=True),
            ),
            (FeedMetadata(name="grypedb", enabled=False), 0, None),
        ],
    )
    def test_get_groups_to_download_grype(
        self,
        metadata: FeedMetadata,
        expected_number_groups: int,
        expected_feed_group_metadata: FeedMetadata,
    ):
        source_feeds = {
            "grypedb": {
                "meta":
                FeedList(feeds=[
                    FeedAPIRecord(
                        name="grypedb",
                        description="grypedb feed",
                        access_tier="0",
                    )
                ]),
                "groups": [
                    FeedAPIGroupRecord(
                        name="grypedb:vulnerabilities",
                        description="grypedb:vulnerabilities group",
                        access_tier="0",
                        grype_listing=GovulnersDBListing(
                            built=nextlinux_now_datetime(),
                            version="2",
                            url="www.next-linux.systems",
                            checksum="sha256:xxx",
                        ),
                    )
                ],
            }
        }
        feeds_to_sync = [GovulnersDBFeed(metadata=metadata)]
        sync_config = {
            "grypedb": SyncConfig(enabled=True, url="www.next-linux.systems")
        }
        groups_to_download = GovulnersDBSyncUtilProvider(
            sync_config).get_groups_to_download(source_feeds, feeds_to_sync,
                                                "0")
        assert len(groups_to_download) == expected_number_groups
        if expected_number_groups > 0:
            group = groups_to_download[0]
            assert group.enabled == expected_feed_group_metadata.enabled
            assert group.feed_name == expected_feed_group_metadata.feed_name
            assert group.name == expected_feed_group_metadata.name

    def test_get_groups_to_download_legacy(self):
        feed_group_metadata = [
            FeedGroupMetadata(name="vulnerabilities:alpine:3.10",
                              enabled=True),
            FeedGroupMetadata(name="vulnerabilities:alpine:3.11",
                              enabled=True),
        ]
        feeds_to_sync = [
            VulnerabilityFeed(metadata=FeedMetadata(
                name="vulnerabilities",
                enabled=True,
                groups=feed_group_metadata,
            ))
        ]
        sync_config = {
            "vulnerabilities":
            SyncConfig(enabled=True, url="www.next-linux.systems")
        }
        groups_to_download = LegacySyncUtilProvider(
            sync_config).get_groups_to_download({}, feeds_to_sync, "0")
        assert groups_to_download == feed_group_metadata
