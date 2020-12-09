from unittest import mock

from spp_cognito_auth import Auth, AuthBlueprint


def test_auth_blueprint_logout(flask_app, client):
    flask_app.auth._session = {"foo": "bar"}
    flask_app.auth._session["state"] = "old-state"
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    response = client.get("/auth/logout")
    assert response.status_code == 302
    assert response.headers["Location"].startswith(
        "https://test-cognito-domain.test.com/logout?"
        + "client_id=test-client-id&"
        + "response_type=code&"
        + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
        + "redirect_uri=http://test-app-host.test.com/auth/callback&"
        + "state="
    )
    assert flask_app.auth._session["state"] != "old-state"
    assert "state" in flask_app.auth._session
    assert len(flask_app.auth._session) == 1


@mock.patch.object(Auth, "process_callback")
def test_auth_blueprint_callback(mock_process_callback, flask_app, client):
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    flask_app.auth._session["state"] = "fake-state-uuid"
    response = client.get("/auth/callback?code=mock-auth-code&state=fake-state-uuid")
    mock_process_callback.assert_called_once_with("mock-auth-code")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/"


@mock.patch.object(Auth, "process_callback")
def test_auth_blueprint_callback_context_redirect(
    mock_process_callback, flask_app, client
):
    flask_app.auth.set_redirect("http://localhost/context-based-url/foobar")
    flask_app.auth._session["state"] = "fake-state-uuid"
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    response = client.get("/auth/callback?code=mock-auth-code&state=fake-state-uuid")
    mock_process_callback.assert_called_once_with("mock-auth-code")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/context-based-url/foobar"


def test_auth_blueprint_callback_no_state(flask_app, client):
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    flask_app.auth._session["state"] = "fake-state-uuid"
    response = client.get("/auth/callback?code=mock-auth-code")
    assert response.status_code == 302
    assert response.headers["Location"].startswith(
        "https://test-cognito-domain.test.com/logout?"
        + "client_id=test-client-id&"
        + "response_type=code&"
        + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
        + "redirect_uri=http://test-app-host.test.com/auth/callback&"
        + "state="
    )
    assert flask_app.auth._session["state"] != "fake-state-uuid"


def test_auth_blueprint_callback_invalid_state(flask_app, client):
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    flask_app.auth._session["state"] = "fake-state-uuid"
    response = client.get("/auth/callback?code=mock-auth-code&state=invalid-state-uuid")
    assert response.status_code == 302
    assert response.headers["Location"].startswith(
        "https://test-cognito-domain.test.com/logout?"
        + "client_id=test-client-id&"
        + "response_type=code&"
        + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
        + "redirect_uri=http://test-app-host.test.com/auth/callback&"
        + "state="
    )
    assert flask_app.auth._session["state"] != "fake-state-uuid"
