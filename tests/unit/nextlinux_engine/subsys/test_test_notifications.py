from nextlinux_engine.subsys import logger
from nextlinux_engine.subsys.notifications import Notification

logger.enable_test_logging()


def test_policy_eval_test_notification_building_works():
    notification = Notification("policy_eval", "sam", "sam@nextlinux.com")
    assert notification.to_json() is not None


def test_tag_update_test_notification_building_works():
    notification = Notification("tag_update", "sam", "sam@nextlinux.com")
    assert notification.to_json() is not None


def test_vuln_update_test_notification_building_works():
    notification = Notification("vuln_update", "sam", "sam@nextlinux.com")
    assert notification.to_json() is not None


def test_analysis_update_test_notification_building_works():
    notification = Notification("analysis_update", "sam", "sam@nextlinux.com")
    assert notification.to_json() is not None
