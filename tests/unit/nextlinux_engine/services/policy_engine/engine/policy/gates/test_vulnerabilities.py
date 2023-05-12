import datetime
import json
import os
import re

import pytest

from nextlinux_engine.common.models.policy_engine import ImageVulnerabilitiesReport
from nextlinux_engine.db import Image
from nextlinux_engine.db.entities.policy_engine import (
    FeedGroupMetadata,
    FeedMetadata,
    GovulnersDBFeedMetadata,
)
from nextlinux_engine.services.policy_engine.engine.policy.gate import ExecutionContext
from nextlinux_engine.services.policy_engine.engine.policy.gates.vulnerabilities import (
    FeedOutOfDateTrigger,
    UnsupportedDistroTrigger,
    VulnerabilitiesGate,
    VulnerabilityBlacklistTrigger,
    VulnerabilityMatchTrigger,
)
from nextlinux_engine.services.policy_engine.engine.vulns.providers import (
    GovulnersProvider,
    LegacyProvider,
)
from tests.unit.nextlinux_engine.clients.test_grype_wrapper import (  # pylint: disable=W0611
    GOVULNERS_DB_VERSION, TestGovulnersWrapperSingleton,
    patch_grype_wrapper_singleton, production_grype_db_dir,
    test_grype_wrapper_singleton,
)


@pytest.fixture
def set_provider(monkeypatch):

    def _set_provider(provider_name=None):
        provider = LegacyProvider
        if provider_name == "grype":
            provider = GovulnersProvider
        monkeypatch.setattr(
            "nextlinux_engine.services.policy_engine.engine.policy.gates.vulnerabilities.get_vulnerabilities_provider",
            lambda: provider(),
        )

    return _set_provider


@pytest.fixture
def load_vulnerabilities_report_file(request):
    module_path = os.path.dirname(request.module.__file__)
    test_name = os.path.splitext(os.path.basename(request.module.__file__))[0]

    def _load_vulnerabilities_report_file(file_name):
        """
        Load a json file containing the vulnerabilities report into an instance of ImageVulnerabilitiesReport.
        The files should all be stored in the tests/unit/nextlinux_engine/services/policy_engine/policy/gates/test_vulnerabilities folder.
        """
        with open(os.path.join(module_path, test_name, file_name)) as file:
            json_data = json.load(file)
        return ImageVulnerabilitiesReport.from_json(json_data)

    return _load_vulnerabilities_report_file


@pytest.fixture
def setup_mocks_vulnerabilities_gate(load_vulnerabilities_report_file,
                                     monkeypatch, set_provider):
    # required for VulnerabilitiesGate.prepare_context
    monkeypatch.setattr(
        "nextlinux_engine.services.policy_engine.engine.policy.gates.vulnerabilities.get_thread_scoped_session",
        lambda: None,
    )

    # required for VulnerabilitiesGate.prepare_context
    # mocks nextlinux_engine.services.policy_engine.engine.vulns.providers.LegacyProvider.get_image_vulnerabilities
    # mocks nextlinux_engine.services.policy_engine.engine.vulns.providers.GovulnersProvider.get_image_vulnerabilities
    # mocks nextlinux_engine.db.session_scope
    def _setup_mocks_vulnerabilities_gate(file_name, provider_name):
        set_provider(provider_name)
        if provider_name == "legacy":
            monkeypatch.setattr(
                "nextlinux_engine.services.policy_engine.engine.vulns.providers.LegacyProvider.get_image_vulnerabilities",
                lambda instance, image, db_session:
                load_vulnerabilities_report_file(file_name),
            )
        if provider_name == "grype":
            monkeypatch.setattr(
                "nextlinux_engine.services.policy_engine.engine.vulns.providers.GovulnersProvider.get_image_vulnerabilities",
                lambda instance, image, db_session:
                load_vulnerabilities_report_file(file_name),
            )

    return _setup_mocks_vulnerabilities_gate


class TestVulnerabilitiesGate:

    @pytest.mark.parametrize(
        "vuln_provider, image_obj, mock_vuln_report, feed_group_metadata, grype_db_feed_metadata, expected_trigger_fired",
        [
            (
                "legacy",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                FeedGroupMetadata(
                    last_sync=datetime.datetime.utcnow() -
                    datetime.timedelta(days=2),
                    name="test-feed-out-of-date",
                ),
                None,
                True,
            ),
            (
                "legacy",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                FeedGroupMetadata(
                    last_sync=datetime.datetime.utcnow(),
                    name="test-feed-not-out-of-date",
                ),
                None,
                False,
            ),
            (
                "grype",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                None,
                GovulnersDBFeedMetadata(built_at=datetime.datetime.now() -
                                        datetime.timedelta(days=2)),
                True,
            ),
            (
                "grype",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                None,
                GovulnersDBFeedMetadata(built_at=datetime.datetime.now()),
                False,
            ),
        ],
    )
    def test_feed_out_of_date_trigger(
        self,
        vuln_provider,
        image_obj,
        mock_vuln_report,
        feed_group_metadata,
        grype_db_feed_metadata,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
        mock_gate_util_provider_feed_data,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, vuln_provider)
        mock_gate_util_provider_feed_data(
            feed_group_metadata=feed_group_metadata,
            grype_db_feed_metadata=grype_db_feed_metadata,
        )
        vulns_gate = VulnerabilitiesGate()
        trigger = FeedOutOfDateTrigger(parent_gate_cls=VulnerabilitiesGate,
                                       max_days_since_sync="1")
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert (
                trigger.fired[0].msg ==
                f"The vulnerability feed for this image distro is older than MAXAGE ({trigger.max_age.value()}) days"
            )

    @pytest.mark.parametrize(
        "vuln_provider, image_obj, mock_vuln_report, feed_metadata, grypedb, expected_trigger_fired",
        [
            (
                "legacy",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                FeedMetadata(name="vulnerabilities",
                             groups=[FeedGroupMetadata(name="debian:10")]),
                None,
                False,
            ),
            (
                "legacy",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                FeedMetadata(name="vulnerabilities",
                             groups=[FeedGroupMetadata(name="debian:9")]),
                None,
                True,
            ),
            (
                "grype",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="9"),
                "debian_1_os_will-fix.json",
                None,
                GovulnersDBFeedMetadata(groups=[{
                    "name": "debian:10",
                    "record_count": 200
                }]),
                True,
            ),
            (
                "grype",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                None,
                GovulnersDBFeedMetadata(groups=[{
                    "name": "debian:10",
                    "record_count": 200
                }]),
                False,
            ),
            (
                "grype",
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                None,
                None,
                True,
            ),
        ],
    )
    def test_unsupported_distro_trigger(
        self,
        vuln_provider,
        image_obj,
        mock_vuln_report,
        feed_metadata,
        grypedb,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
        mock_gate_util_provider_feed_data,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, vuln_provider)
        mock_gate_util_provider_feed_data(feed_metadata=feed_metadata,
                                          grype_db_feed_metadata=grypedb)
        vulns_gate = VulnerabilitiesGate()
        trigger = UnsupportedDistroTrigger(parent_gate_cls=VulnerabilitiesGate)
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert (
                trigger.fired[0].msg ==
                f"Distro-specific feed data not found for distro namespace: {image_obj.distro_namespace}. Cannot perform CVE scan OS/distro packages"
            )

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, vulnerability_ids, vendor_only, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "CVE-2020-13529",  # One matching vuln
                "false",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "CVE-2020-13579",  # One fake vuln
                "false",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "CVE-2020-13529",  # One matching vulns (not a won't fix)
                "true",  # Vendor only
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_wont-fix.json",
                "CVE-2020-15719",  # One matching vulns (was changed to won't fix for the purposes of this test)
                "true",  # Vendor only
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "CVE-2020-13529, CVE-2020-13579",  # One matching vuln and one fake vuln
                "false",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "CVE-2020-13525, CVE-2004-0975",  # Two fake vulns
                "false",
                False,
            ),
        ],
    )
    def test_vulnerabilities_blacklist_trigger(
        self,
        image_obj,
        mock_vuln_report,
        vulnerability_ids,
        vendor_only,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityBlacklistTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            vulnerability_ids=vulnerability_ids,
            vendor_only=vendor_only,
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert re.fullmatch(
                r"Blacklisted vulnerabilities detected: \[((\'CVE-\d{4}-\d{4,}\')(, )?)+]",
                trigger.fired[0].msg,
            )

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, fix_available, expected_trigger_fired, expected_number_triggers",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_fix-available.json",
                "true",
                True,
                1,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_fix-available.json",
                "false",
                False,
                0,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "true",
                False,
                0,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "false",
                True,
                1,
            ),
        ],
    )
    def test_vulnerability_match_trigger_fix_available(
        self,
        image_obj,
        mock_vuln_report,
        fix_available,
        expected_trigger_fired,
        expected_number_triggers,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            fix_available=fix_available,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        assert len(trigger.fired) == expected_number_triggers

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, vendor_only, expected_trigger_fired, expected_number_triggers",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "true",
                True,
                1,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "false",
                True,
                1,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_wont-fix.json",
                "true",
                False,
                0,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_wont-fix.json",
                "false",
                True,
                1,
            ),
        ],
    )
    def test_vulnerability_match_trigger_vendor_only(
        self,
        image_obj,
        mock_vuln_report,
        vendor_only,
        expected_trigger_fired,
        expected_number_triggers,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            vendor_only=vendor_only,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        assert len(trigger.fired) == expected_number_triggers

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, max_days_since_creation, expected_trigger_fired, expected_number_triggers",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "1000000",
                False,
                0,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "0",
                True,
                1,
            ),
        ],
    )
    def test_vulnerability_match_trigger_max_days_since_creation(
        self,
        image_obj,
        mock_vuln_report,
        max_days_since_creation,
        expected_trigger_fired,
        expected_number_triggers,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            max_days_since_creation=max_days_since_creation,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        assert len(trigger.fired) == expected_number_triggers

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, max_days_since_fix, expected_trigger_fired, expected_number_triggers",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_fix-available.json",
                "1000000",
                False,
                0,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_fix-available.json",
                "0",
                True,
                1,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "1000000",
                False,
                0,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "0",
                False,
                0,
            ),
        ],
    )
    def test_vulnerability_match_trigger_max_days_since_fix(
        self,
        image_obj,
        mock_vuln_report,
        max_days_since_fix,
        expected_trigger_fired,
        expected_number_triggers,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            max_days_since_creation=max_days_since_fix,
            fix_available="true",
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        assert len(trigger.fired) == expected_number_triggers

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, package_path_exclude, expected_trigger_fired, expected_number_triggers",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_non-os_will-fix.json",
                "/usr/.*",
                True,
                1,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_non-os_will-fix.json",
                "/bin/.*",
                False,
                0,
            ),
        ],
    )
    def test_vulnerability_match_trigger_package_path_exclude(
        self,
        image_obj,
        mock_vuln_report,
        package_path_exclude,
        expected_trigger_fired,
        expected_number_triggers,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            package_path_exclude=package_path_exclude,
            package_type="non-os",
            vendor_only=False,
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        assert len(trigger.fired) == expected_number_triggers

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, package_type, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "all",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "os",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_non-os_will-fix.json",
                "os",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "non-os",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_non-os_will-fix.json",
                "non-os",
                True,
            ),
        ],
    )
    def test_vulnerability_match_trigger_package_type(
        self,
        image_obj,
        mock_vuln_report,
        package_type,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate, package_type=package_type)
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, severity_comparison, severity, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "unknown",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "negligible",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "low",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "medium",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "high",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "critical",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<",
                "medium",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">",
                "medium",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "!=",
                "medium",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<=",
                "medium",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">=",
                "medium",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<",
                "unknown",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">",
                "critical",
                False,
            ),
        ],
    )
    def test_vulnerability_match_trigger_severity_comparison(
        self,
        image_obj,
        mock_vuln_report,
        severity_comparison,
        severity,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            severity_comparison=severity_comparison,
            severity=severity,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, score_comparison, base_score, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">",
                "6.0",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<",
                "6.0",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "6.0",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">=",
                "6.0",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<=",
                "6.0",
                False,
            ),
        ],
    )
    def test_vulnerability_match_trigger_cvssv3_base_score_comparison(
        self,
        image_obj,
        mock_vuln_report,
        score_comparison,
        base_score,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            cvss_v3_base_score_comparison=score_comparison,
            cvss_v3_base_score=base_score,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, score_comparison, exploitability_score, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">",
                "3.8",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<",
                "3.8",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "3.8",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">=",
                "3.8",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<=",
                "3.8",
                True,
            ),
        ],
    )
    def test_vulnerability_match_trigger_cvssv3_exploitability_score_comparison(
        self,
        image_obj,
        mock_vuln_report,
        score_comparison,
        exploitability_score,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            cvss_v3_exploitability_score_comparison=score_comparison,
            cvss_v3_exploitability_score=exploitability_score,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, score_comparison, impact_score, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">",
                "3.6",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<",
                "3.6",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "=",
                "3.6",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                ">=",
                "3.6",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix.json",
                "<=",
                "3.6",
                False,
            ),
        ],
    )
    def test_vulnerability_match_trigger_cvssv3_impact_score_comparison(
        self,
        image_obj,
        mock_vuln_report,
        score_comparison,
        impact_score,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            cvss_v3_impact_score_comparison=score_comparison,
            cvss_v3_impact_score=impact_score,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, score_comparison, base_score, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                ">",
                "6.0",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "<",
                "6.0",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "=",
                "6.0",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                ">=",
                "6.0",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "<=",
                "6.0",
                False,
            ),
        ],
    )
    def test_vulnerability_match_trigger_vendor_cvssv3_base_score_comparison(
        self,
        image_obj,
        mock_vuln_report,
        score_comparison,
        base_score,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            vendor_cvss_v3_base_score_comparison=score_comparison,
            vendor_cvss_v3_base_score=base_score,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, score_comparison, exploitability_score, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                ">",
                "3.8",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "<",
                "3.8",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "=",
                "3.8",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                ">=",
                "3.8",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "<=",
                "3.8",
                True,
            ),
        ],
    )
    def test_vulnerability_match_trigger_vendor_cvssv3_exploitability_score_comparison(
        self,
        image_obj,
        mock_vuln_report,
        score_comparison,
        exploitability_score,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            vendor_cvss_v3_exploitability_score_comparison=score_comparison,
            vendor_cvss_v3_exploitability_score=exploitability_score,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0

    @pytest.mark.parametrize(
        "image_obj, mock_vuln_report, score_comparison, impact_score, expected_trigger_fired",
        [
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                ">",
                "3.6",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "<",
                "3.6",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "=",
                "3.6",
                False,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                ">=",
                "3.6",
                True,
            ),
            (
                Image(id="1",
                      user_id="admin",
                      distro_name="debian",
                      distro_version="10"),
                "debian_1_os_will-fix_vendor_cvssv3.json",
                "<=",
                "3.6",
                False,
            ),
        ],
    )
    def test_vulnerability_match_trigger_vendor_cvssv3_impact_score_comparison(
        self,
        image_obj,
        mock_vuln_report,
        score_comparison,
        impact_score,
        expected_trigger_fired,
        setup_mocks_vulnerabilities_gate,
    ):
        setup_mocks_vulnerabilities_gate(mock_vuln_report, "legacy")
        vulns_gate = VulnerabilitiesGate()
        trigger = VulnerabilityMatchTrigger(
            parent_gate_cls=VulnerabilitiesGate,
            vendor_cvss_v3_impact_score_comparison=score_comparison,
            vendor_cvss_v3_impact_score=impact_score,
            package_type="all",
        )
        exec_context = ExecutionContext(db_session=None, configuration={})
        vulns_gate.prepare_context(image_obj, exec_context)
        trigger.evaluate(image_obj, exec_context)
        assert trigger.did_fire == expected_trigger_fired
        if expected_trigger_fired:
            assert len(trigger.fired) == 1
        else:
            assert len(trigger.fired) == 0
