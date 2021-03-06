from datetime import datetime, timedelta
from unittest import mock

import pytest
from authlib.jose.errors import ExpiredTokenError
from authlib.oauth2.rfc6749 import OAuth2Token
from freezegun import freeze_time
from helpers import is_valid_uuid

import spp_cognito_auth
from spp_cognito_auth import new_oauth_client


class TestAuth:
    @mock.patch.object(spp_cognito_auth.Auth, "generate_state")
    def test_login_url(self, mock_generate_state, auth):
        mock_generate_state.return_value = "my-random-uuid"
        assert auth.login_url() == (
            "https://test-cognito-domain.test.com/login?"
            + "client_id=test-client-id&"
            + "response_type=code&"
            + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
            + "redirect_uri=http://test-app-host.test.com/auth/callback&"
            + "state=my-random-uuid"
        )

    @mock.patch.object(spp_cognito_auth.Auth, "generate_state")
    def test_logout_url(self, mock_generate_state, auth):
        mock_generate_state.return_value = "my-random-uuid"
        assert auth.logout_url() == (
            "https://test-cognito-domain.test.com/logout?"
            + "client_id=test-client-id&"
            + "response_type=code&"
            + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
            + "redirect_uri=http://test-app-host.test.com/auth/callback&"
            + "state=my-random-uuid"
        )

    def test_public_key_url(self, auth):
        assert (
            auth.public_key_url()
            == "https://test-cognito-endpoint.test.com/.well-known/jwks.json"
        )
        assert auth.token_url() == "https://test-cognito-domain.test.com/oauth2/token"

    def test_get_auth_token(self, auth, oauth):
        oauth.fetch_token.return_value = OAuth2Token(params={})
        assert type(auth.get_auth_token("fake-auth-code")) is OAuth2Token
        oauth.fetch_token.assert_called_once_with(
            "https://test-cognito-domain.test.com/oauth2/token",
            grant_type="authorization_code",
            code="fake-auth-code",
            authorization_response="http://test-app-host.test.com/auth/callback",
        )

    @freeze_time("2020-11-13")
    def test_get_public_keys(self, auth, jwks, requests_mock):
        requests_mock.get(
            auth.public_key_url(),
            json=jwks,
            headers={"cache-control": "public, max-age=86400"},
        )
        assert auth.get_public_keys() == jwks
        assert auth._jwks_expires_at.isoformat() == "2020-11-14T00:00:00"

    @freeze_time("2020-11-13")
    def test_get_public_keys_no_expiry_old_token(self, auth, jwks, requests_mock):
        requests_mock.get(
            auth.public_key_url(),
            json=jwks,
            headers={"cache-control": "public, max-age=86400"},
        )
        auth._jwks_token = {"foo": "bar"}
        assert auth.get_public_keys() == jwks
        assert auth._jwks_expires_at.isoformat() == "2020-11-14T00:00:00"

    @freeze_time("2020-11-13")
    def test_get_public_keys_old_expiry_old_token(self, auth, jwks, requests_mock):
        requests_mock.get(
            auth.public_key_url(),
            json=jwks,
            headers={"cache-control": "public, max-age=86400"},
        )
        auth._jwks_token = {"foo": "bar"}
        auth._jwks_expires_at = datetime(1970, 1, 1)
        assert auth.get_public_keys() == jwks
        assert auth._jwks_expires_at.isoformat() == "2020-11-14T00:00:00"

    @freeze_time("2020-11-13")
    def test_get_public_keys_not_expired(self, auth, jwks):
        auth._jwks_token = jwks
        auth._jwks_expires_at = datetime.now() + timedelta(hours=1)
        assert auth.get_public_keys() == jwks
        assert auth._jwks_expires_at.isoformat() == "2020-11-13T01:00:00"

    @mock.patch.object(spp_cognito_auth.Auth, "get_auth_token")
    @mock.patch.object(spp_cognito_auth.Auth, "get_public_keys")
    @mock.patch("authlib.jose.jwt.decode")
    def test_process_callback(
        self, mock_jwt_decode, mock_get_public_keys, mock_get_auth_token, auth, jwks
    ):
        mock_get_auth_token.return_value = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_at": "mock-expires-at",
        }
        mock_jwt_decode.return_value = {
            "username": "mock-user",
            "cognito:groups": ["survey.main.read", "survey.main.write"],
        }
        mock_get_public_keys.return_value = jwks
        auth._session = {}
        auth.process_callback("fake-auth-code")
        mock_get_auth_token.assert_called_once_with("fake-auth-code")
        mock_jwt_decode.assert_called_once_with("mock-access-token", jwks)
        mock_get_public_keys.assert_called_once()
        assert auth._session["access_token"] == "mock-access-token"
        assert auth._session["refresh_token"] == "mock-refresh-token"
        assert auth._session["expires_at"] == "mock-expires-at"
        assert auth._session["username"] == "mock-user"
        assert auth._session["roles"] == ["survey.main.read", "survey.main.write"]

    @mock.patch.object(spp_cognito_auth.Auth, "get_auth_token")
    @mock.patch.object(spp_cognito_auth.Auth, "get_public_keys")
    @mock.patch("authlib.jose.jwt.decode")
    def test_process_callback_no_groups(
        self, mock_jwt_decode, mock_get_public_keys, mock_get_auth_token, auth, jwks
    ):
        mock_get_auth_token.return_value = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_at": "mock-expires-at",
        }
        mock_jwt_decode.return_value = {
            "username": "mock-user",
        }
        mock_get_public_keys.return_value = jwks
        auth._session = {}
        auth.process_callback("fake-auth-code")
        mock_get_auth_token.assert_called_once_with("fake-auth-code")
        mock_jwt_decode.assert_called_once_with("mock-access-token", jwks)
        mock_get_public_keys.assert_called_once()
        assert auth._session["access_token"] == "mock-access-token"
        assert auth._session["refresh_token"] == "mock-refresh-token"
        assert auth._session["expires_at"] == "mock-expires-at"
        assert auth._session["username"] == "mock-user"
        assert auth._session["roles"] == []

    def test_get_username(self, auth):
        auth._session = {"username": "test-user"}
        assert auth.get_username() == "test-user"

    def test_get_username_none(self, auth):
        auth._session = {}
        assert auth.get_username() is None

    def test_get_roles(self, auth):
        auth._session = {"roles": ["survey.main.read", "survey.main.write"]}
        assert auth.get_roles() == ["survey.main.read", "survey.main.write"]

    def test_get_roles_none(self, auth):
        auth._session = {}
        assert auth.get_roles() == []

    def test_get_redirect(self, auth):
        auth._session = {"redirect_url": "/foobar"}
        assert auth.get_redirect() == "/foobar"

    def test_get_redirect_none(self, auth):
        auth._session = {}
        assert auth.get_redirect() is None

    def test_set_redirect(self, auth):
        auth._session = {}
        auth.set_redirect("/foobar")
        assert auth._session["redirect_url"] == "/foobar"

    @mock.patch.object(spp_cognito_auth.Auth, "get_public_keys")
    @mock.patch("authlib.jose.jwt.decode")
    def test_logged_in(self, mock_jwt_decode, mock_get_public_keys, auth):
        auth._session = {"access_token": "my-token"}
        assert auth.logged_in() is True

    def test_logged_in_no_token(self, auth):
        auth._session = {}
        assert auth.logged_in() is False

    @mock.patch.object(spp_cognito_auth.Auth, "get_public_keys")
    @mock.patch("authlib.jose.jwt.decode")
    def test_logged_in_expired(self, mock_jwt_decode, mock_get_public_keys, auth):
        mock_token = mock.MagicMock()
        mock_jwt_decode.return_value = mock_token
        mock_token.validate.side_effect = ExpiredTokenError()
        auth._session = {"access_token": "my-token"}
        assert auth.logged_in() is False

    @mock.patch.object(spp_cognito_auth.Auth, "get_public_keys")
    @mock.patch("authlib.jose.jwt.decode")
    def test_logged_in_error(self, mock_jwt_decode, mock_get_public_keys, auth):
        auth._session = {"access_token": "my-token"}
        mock_token = mock.MagicMock()
        mock_jwt_decode.return_value = mock_token
        mock_token.validate.side_effect = Exception("foobar")
        with pytest.raises(Exception) as err:
            auth.logged_in()
        assert str(err.value) == "foobar"

    def test_logout(self, auth):
        auth._session = {"access_token": "my-token"}
        auth.logout()
        assert auth._session == {}

    @pytest.mark.parametrize(
        "role_matcher,roles,expected",
        [
            ("survey.main.read", ["survey.main.read"], True),
            ("survey.main.write", ["survey.main.read"], False),
            ("survey.*.read", ["survey.main.read"], True),
            ("survey.*.*", ["survey.main.write"], True),
            ("survey.*.write", ["survey.main.read"], False),
            (
                "survey.*.read",
                ["survey.secondary.read", "survey.main.write", "survey.main.read"],
                True,
            ),
            ("survey.*.read", ["survey.main.write", "survey.main.read"], True),
            ("survey.main.read", ["survey.secondary.read", "survey.main.read"], True),
        ],
    )
    def test_match_role(self, role_matcher, roles, expected, auth):
        auth._session["roles"] = roles
        assert auth.match_role(role_matcher) is expected

    @pytest.mark.parametrize(
        "role_matchers,roles,expected",
        [
            (["survey.main.write", "survey.main.read"], ["survey.main.read"], True),
            (
                ["survey.main.write", "survey.*.write", "dev"],
                ["survey.main.read"],
                False,
            ),
        ],
    )
    def test_has_permission(self, role_matchers, roles, expected, auth):
        auth._session["roles"] = roles
        assert auth.has_permission(role_matchers) is expected

    def test_generate_state(self, auth):
        state = auth.generate_state()
        assert is_valid_uuid(state)
        assert is_valid_uuid(auth._session["state"])
        assert auth._session["state"] == state

    def test_validate_state(self, auth):
        auth._session["state"] = "fake-state"
        assert auth.validate_state("fake-state") is True

    def test_validate_state_invalid(self, auth):
        auth._session["state"] = "fake-state"
        assert auth.validate_state("invalid-state") is False


def test_new_oauth_client(config):
    oauth2_session = new_oauth_client(config)
    assert oauth2_session.client_id == config.client_id
    assert oauth2_session.client_secret == config.client_secret
    assert oauth2_session.redirect_uri == config.callback_url
