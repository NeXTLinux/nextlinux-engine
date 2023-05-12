import datetime

import pytest

from nextlinux_engine.db.entities.common import nextlinux_now_datetime
from nextlinux_engine.services.policy_engine.engine.policy.bundles import (
    ExecutableWhitelistItem, )
from nextlinux_engine.util.time import datetime_to_rfc3339


class TestExecutableWhitelistItem:

    ten_min_ago = datetime_to_rfc3339(nextlinux_now_datetime() -
                                      datetime.timedelta(minutes=10))
    ten_min_from_now = datetime_to_rfc3339(nextlinux_now_datetime() +
                                           datetime.timedelta(minutes=10))

    @pytest.mark.parametrize("expires_on,expected",
                             [(ten_min_ago, True), (ten_min_from_now, False)])
    def test_is_expired(self, expires_on, expected):
        item_json = {"expires_on": expires_on, "gate": "fake_gate"}
        item = ExecutableWhitelistItem(item_json, None)
        assert item.is_expired() == expected

    @pytest.mark.parametrize(
        "expires_on,exception,expected",
        [(None, None, False), ("", None, False),
         ("2020-10-15", Exception, None)],
    )
    def test_is_expired_bad_input(self, expires_on, exception, expected):
        if exception:
            with pytest.raises(exception):
                item_json = {"expires_on": expires_on, "gate": "fake_gate"}
                ExecutableWhitelistItem(item_json, None)
        else:
            item_json = {"expires_on": expires_on, "gate": "fake_gate"}
            item = ExecutableWhitelistItem(item_json, None)
            assert item.is_expired() == expected
