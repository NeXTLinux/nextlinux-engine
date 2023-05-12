import pytest

<<<<<<< HEAD:tests/unit/nextlinux_engine/services/policy_engine/engine/vulns/test_scanners.py
from nextlinux_engine.services.policy_engine.engine.vulns.scanners import GrypeScanner
=======
from nextlinux_engine.services.policy_engine.engine.vulns.scanners import GovulnersScanner
>>>>>>> master:tests/unit/anchore_engine/services/policy_engine/engine/vulns/test_scanners.py


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ("nvd", True),
        ("nvdv2", True),
        (["nvdv2:cves"], True),
        ("", False),
        (["nvd", "test"], False),
        (["test"], False),
    ],
)
def test_is_only_nvd_namespace(input, expected_output):
    """
    Tests private function in GovulnersScanner that determines if namespace is an nvd namespace
    """
    assert GovulnersScanner()._is_only_nvd_namespace(input) is expected_output
