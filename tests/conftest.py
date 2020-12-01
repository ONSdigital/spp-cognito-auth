from unittest import mock

import pytest

from spp_cognito_auth import Auth, AuthConfig


@pytest.fixture
def config():
    return AuthConfig(
        client_id="test-client-id",
        client_secret="test-client-secret",
        callback_url="http://test-app-host.test.com/auth/callback",
        cognito_domain="https://test-cognito-domain.test.com",
        cognito_endpoint="https://test-cognito-endpoint.test.com",
    )


@pytest.fixture
def oauth():
    return mock.MagicMock()


@pytest.fixture
def auth(config, oauth):
    return Auth(config, oauth, None)


@pytest.fixture
def jwks():
    return {
        "keys": [
            {
                "alg": "RS256",
                "e": "AQAB",
                "kid": "abcdefghijklmnopqrsexample=",
                "kty": "RSA",
                "n": "lsjhglskjhgslkjgh43lj5h34lkjh34lkjht3example",
                "use": "sig",
            }
        ]
    }
