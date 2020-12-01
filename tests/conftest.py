from unittest import mock

import pytest
from flask import Flask

from spp_cognito_auth import Auth, AuthConfig, requires_auth


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
def auth(config, oauth, session):
    return Auth(config, oauth, session)


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


@pytest.fixture
def session():
    return {}


@pytest.fixture
def flask_app(auth):
    app = Flask(__name__)
    app.secret_key = "my-secret-key"
    app.auth = auth

    @app.route("/")
    @requires_auth
    def root():
        return "Hello, World!"

    with app.app_context():
        yield app


@pytest.fixture
def client(flask_app):
    ctx = flask_app.test_request_context()
    ctx.push()
    return flask_app.test_client()
