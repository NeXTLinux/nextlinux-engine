from dataclasses import dataclass
from typing import List

import pytest

from nextlinux_engine.configuration import localconfig
from nextlinux_engine.services.policy_engine.engine.feeds.config import (
    compute_selected_configs_to_sync,
    get_provider_name,
    get_section_for_vulnerabilities,
    is_sync_enabled,
)
from nextlinux_engine.services.policy_engine.engine.vulns.providers import (
    GrypeProvider,
    LegacyProvider,
)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param({}, {}, id="invalid-emtpy-1"),
        pytest.param(
            {"something": {"feeds": {"nothing": True}}}, {}, id="invalid-empty-2"
        ),
        pytest.param(
            {"services": {"policy_engine": {"vulnerabilities": {}}}},
            {},
            id="valid-empty",
        ),
        pytest.param(
            {"services": {"policy_engine": {"vulnerabilities": "something"}}},
            "something",
            id="valid-not-empty",
        ),
    ],
)
def test_get_feeds_config(test_input, expected):
    localconfig.localconfig = test_input
    assert get_section_for_vulnerabilities() == expected


@pytest.mark.parametrize(
    "provider,test_config,expected",
    [
        pytest.param(
            LegacyProvider, {}, {"vulnerabilities", "nvdv2"}, id="invalid-empty"
        ),
        pytest.param(
            LegacyProvider, None, {"vulnerabilities", "nvdv2"}, id="invalid-none"
        ),
        pytest.param(
            LegacyProvider,
            {"a": {"b": {"c": "d"}}},
            {"vulnerabilities", "nvdv2"},
            id="invalid-gibberish",
        ),
        pytest.param(
            LegacyProvider,
            {"sync": {}},
            {"vulnerabilities", "nvdv2"},
            id="invalid-empty-sync",
        ),
        pytest.param(
            LegacyProvider,
            {"sync": {"data": {}}},
            {"vulnerabilities", "nvdv2"},
            id="invalid-empty-data",
        ),
        pytest.param(
            LegacyProvider,
            {"provider": "legacy", "sync": {"data": {}}},
            {"vulnerabilities", "nvdv2"},
            id="invalid-provider-legacy",
        ),
        pytest.param(
            GrypeProvider,
            {"provider": "govulners", "sync": {"data": {}}},
            {"govulnersdb"},
            id="invalid-provider-govulners",
        ),
    ],
)
def test_get_selected_configs_to_sync_defaults(provider, test_config, expected):
    assert (
        set(
            compute_selected_configs_to_sync(
                provider.__config__name__,
                test_config,
                provider.__default_sync_config__,
            ).keys()
        )
        == expected
    )


@pytest.mark.parametrize(
    "provider, test_config, expected",
    [
        pytest.param(
            LegacyProvider,
            {"provider": "legacy", "sync": {"data": {"packages": {"enabled": True}}}},
            {"packages"},
            id="valid-legacy-packages",
        ),
        pytest.param(
            LegacyProvider,
            {"provider": "legacy", "sync": {"data": {"github": {"enabled": True}}}},
            {"github"},
            id="valid-legacy-github",
        ),
        pytest.param(
            LegacyProvider,
            {
                "provider": "legacy",
                "sync": {"data": {"vulnerabilities": {"enabled": True}}},
            },
            {"vulnerabilities"},
            id="valid-legacy-vulnerabilities",
        ),
        pytest.param(
            LegacyProvider,
            {"provider": "legacy", "sync": {"data": {"nvdv2": {"enabled": True}}}},
            {"nvdv2"},
            id="valid-legacy-nvdv2",
        ),
        pytest.param(
            LegacyProvider,
            {"provider": "legacy", "sync": {"data": {"vulndb": {"enabled": True}}}},
            set(),
            id="invalid-legacy-vulndb",
        ),
        pytest.param(
            GrypeProvider,
            {"provider": "govulners", "sync": {"data": {"govulnersdb": {"enabled": True}}}},
            {"govulnersdb"},
            id="valid-govulners-govulnersdb",
        ),
        pytest.param(
            GrypeProvider,
            {"provider": "govulners", "sync": {"data": {"github": {"enabled": True}}}},
            set(),
            id="invalid-govulners-github",
        ),
        pytest.param(
            GrypeProvider,
            {
                "provider": "govulners",
                "sync": {"data": {"vulnerabilities": {"enabled": True}}},
            },
            set(),
            id="invalid-govulners-vulnerabilities",
        ),
        pytest.param(
            GrypeProvider,
            {"provider": "govulners", "sync": {"data": {"nvdv2": {"enabled": True}}}},
            set(),
            id="invalid-govulners-nvdv2",
        ),
        pytest.param(
            GrypeProvider,
            {"provider": "govulners", "sync": {"data": {"vulndb": {"enabled": True}}}},
            set(),
            id="invalid-govulners-vulndb",
        ),
        pytest.param(
            LegacyProvider,
            {"provider": "legacy", "sync": {"data": {"govulnersdb": {"enabled": True}}}},
            set(),
            id="invalid-legacy-govulnersdb",
        ),
    ],
)
def test_get_selected_configs_to_sync_valid_data(provider, test_config, expected):
    assert (
        set(
            compute_selected_configs_to_sync(
                provider.__config__name__, test_config, provider.__default_sync_config__
            ).keys()
        )
        == expected
    )


@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param(
            {},
            None,
            id="invalid-empty",
        ),
        pytest.param(
            None,
            None,
            id="invalid-none",
        ),
        pytest.param(
            {"provider": "foobar"},
            "foobar",
            id="invalid-provider",
        ),
        pytest.param(
            {"foo": {"bar": {"x": "y"}}},
            None,
            id="invalid-data",
        ),
        pytest.param(
            {"provider": "legacy"},
            "legacy",
            id="valid-legacy",
        ),
        pytest.param(
            {"provider": "govulners"},
            "govulners",
            id="valid-govulners",
        ),
    ],
)
def test_get_provider(test_input, expected):
    assert get_provider_name(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param(
            {},
            True,
            id="invalid-empty",
        ),
        pytest.param(
            None,
            True,
            id="invalid-none",
        ),
        pytest.param(
            {"sync": {"enabled": True}},
            True,
            id="valid-true",
        ),
        pytest.param(
            {"sync": {"enabled": False}},
            False,
            id="valid-false",
        ),
        pytest.param(
            {"sync": {"enabled": "foobar"}},
            True,
            id="valid-gibberish",
        ),
    ],
)
def test_is_sync_enabled(test_input, expected):
    assert is_sync_enabled(test_input) == expected


@dataclass
class FeedConfiguration:
    feed_name: str
    enabled: bool


def get_config_for_params(provider: str, feed_configurations: List[FeedConfiguration]):
    return {
        "provider": provider,
        "sync": {
            "enabled": True,
            "ssl_verify": True,
            "connection_timeout_seconds": 3,
            "read_timeout_seconds": 60,
            "data": {
                feed_configuration.feed_name: {
                    "enabled": feed_configuration.enabled,
                    "url": "www.nextlinux.com",
                }
                for feed_configuration in feed_configurations
            },
        },
    }


@pytest.mark.parametrize(
    "provider, feed_configurations, expected_to_sync_after_compute",
    [
        (  # Legacy provider with one invalid config (vulndb), one govulners config, and two legacy configs
            "legacy",
            [
                FeedConfiguration("vulnerabilities", True),
                FeedConfiguration("nvdv2", True),
                FeedConfiguration("vulndb", True),
                FeedConfiguration("govulnersdb", True),
            ],
            ["nvdv2", "vulnerabilities"],
        ),
        (  # Grype provider with one invalid config (vulndb) one govulners config, and two legacy configs
            "govulners",
            [
                FeedConfiguration("vulnerabilities", True),
                FeedConfiguration("nvdv2", True),
                FeedConfiguration("vulndb", True),
                FeedConfiguration("govulnersdb", True),
            ],
            ["govulnersdb"],
        ),
        (  # Legacy provider with two disabled configs and one govulnersdb config that is enabled
            "legacy",
            [
                FeedConfiguration("vulnerabilities", False),
                FeedConfiguration("nvdv2", False),
                FeedConfiguration("govulnersdb", True),
            ],
            [],
        ),
        (  # Grype provider disabled govulnersdb config and two legacy configs enabled
            "govulners",
            [
                FeedConfiguration("vulnerabilities", True),
                FeedConfiguration("nvdv2", True),
                FeedConfiguration("govulnersdb", False),
            ],
            [],
        ),
        (  # Legacy provider all disabled configs
            "legacy",
            [
                FeedConfiguration("vulnerabilities", False),
                FeedConfiguration("nvdv2", False),
                FeedConfiguration("govulnersdb", False),
            ],
            [],
        ),
        (  # Grype provider with all disabled configs
            "govulners",
            [
                FeedConfiguration("vulnerabilities", False),
                FeedConfiguration("nvdv2", False),
                FeedConfiguration("govulnersdb", False),
            ],
            [],
        ),
        (  # Grype provider with packages and govulnersdb enabled
            "govulners",
            [
                FeedConfiguration("vulnerabilities", False),
                FeedConfiguration("nvdv2", False),
                FeedConfiguration("govulnersdb", True),
                FeedConfiguration("packages", True),
            ],
            ["govulnersdb", "packages"],
        ),
        (  # legacy provider with packages and govulnersdb enabled
            "legacy",
            [
                FeedConfiguration("vulnerabilities", False),
                FeedConfiguration("nvdv2", False),
                FeedConfiguration("govulnersdb", True),
                FeedConfiguration("packages", True),
            ],
            ["packages"],
        ),
    ],
)
def test_compute_selected_configs_to_sync(
    provider: str,
    feed_configurations: List[FeedConfiguration],
    expected_to_sync_after_compute: List[str],
):
    if provider == "legacy":
        vulnerabilities_provider = LegacyProvider()
    else:
        vulnerabilities_provider = GrypeProvider()
    sync_configs = compute_selected_configs_to_sync(
        provider=vulnerabilities_provider.get_config_name(),
        vulnerabilities_config=get_config_for_params(provider, feed_configurations),
        default_provider_sync_config=vulnerabilities_provider.get_default_sync_config(),
    )
    assert set(sync_configs.keys()) == set(expected_to_sync_after_compute)
