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
def auth(config):
    return Auth(config, None, None)
