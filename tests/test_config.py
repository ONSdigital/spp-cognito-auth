import os
from unittest import mock

from spp_cognito_auth import AuthConfig
from spp_cognito_auth.config import DEFAULT_SCOPES


@mock.patch.dict(
    os.environ,
    {
        "CLIENT_ID": "client-id",
        "CLIENT_SECRET": "client-secret",
        "CALLBACK_URL": "callback-url",
        "COGNITO_DOMAIN": "cognito-domain",
        "COGNITO_ENDPOINT": "cognito-endpoint",
        "COGNITO_STATE": "123_redirect=https://www.example.com"
    },
)
def test_from_env():
    auth_config = AuthConfig.from_env()
    assert auth_config.client_id == "client-id"
    assert auth_config.client_secret == "client-secret"
    assert auth_config.callback_url == "callback-url"
    assert auth_config.cognito_domain == "cognito-domain"
    assert auth_config.cognito_endpoint == "cognito-endpoint"
    assert auth_config.cognito_scopes == DEFAULT_SCOPES


def test_init():
    auth_config = AuthConfig(
        client_id="client-id",
        client_secret="client-secret",
        callback_url="callback-url",
        cognito_domain="cognito-domain",
        cognito_endpoint="cognito-endpoint",
        cognito_scopes=["cognito-scopes"],
        cognito_state="123_redirect=https://www.example.com"
    )
    assert auth_config.client_id == "client-id"
    assert auth_config.client_secret == "client-secret"
    assert auth_config.callback_url == "callback-url"
    assert auth_config.cognito_domain == "cognito-domain"
    assert auth_config.cognito_endpoint == "cognito-endpoint"
    assert auth_config.cognito_scopes == ["cognito-scopes"]


def test_init_has_default_scopes():
    auth_config = AuthConfig(
        client_id="client-id",
        client_secret="client-secret",
        callback_url="callback-url",
        cognito_domain="cognito-domain",
        cognito_endpoint="cognito-endpoint",
        cognito_state="123_redirect=https://www.example.com"
    )
    assert auth_config.client_id == "client-id"
    assert auth_config.client_secret == "client-secret"
    assert auth_config.callback_url == "callback-url"
    assert auth_config.cognito_domain == "cognito-domain"
    assert auth_config.cognito_endpoint == "cognito-endpoint"
    assert auth_config.cognito_scopes == DEFAULT_SCOPES
