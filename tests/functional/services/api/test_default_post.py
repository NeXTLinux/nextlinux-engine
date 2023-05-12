from tests.functional.services.utils.http_utils import (
    APIResponse,
    get_api_conf,
    http_post_url_encoded,
)


class TestDefaultAPIPostReturns200:

    # @pytest.mark.skip(reason = "Need to figure out how to enable Oauth in config")
    def test_add_oauth_token(self):
        api_conf = get_api_conf()
        payload = {
            "grant_type": "password",
            "username": api_conf["NEXTLINUX_API_USER"],
            "password": api_conf["NEXTLINUX_API_PASS"],
            "client_id": "anonymous",
        }
        resp = http_post_url_encoded(["oauth", "token"], payload)
        assert resp == APIResponse(200)
