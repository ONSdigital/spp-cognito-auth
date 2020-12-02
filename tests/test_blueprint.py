from unittest import mock

from spp_cognito_auth import Auth, AuthBlueprint


def test_auth_blueprint_logout(flask_app, client):
    flask_app.auth._session = {"foo": "bar"}
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    response = client.get("/auth/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == flask_app.auth.logout_url()
    assert flask_app.auth._session == {}


@mock.patch.object(Auth, "process_callback")
def test_auth_blueprint_callback(mock_process_callback, flask_app, client):
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    response = client.get("/auth/callback?code=mock-auth-code")
    mock_process_callback.assert_called_once_with("mock-auth-code")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/"


@mock.patch.object(Auth, "process_callback")
def test_auth_blueprint_callback_context_redirect(
    mock_process_callback, flask_app, client
):
    flask_app.auth.set_redirect("http://localhost/context-based-url/foobar")
    flask_app.register_blueprint(AuthBlueprint().blueprint())
    response = client.get("/auth/callback?code=mock-auth-code")
    mock_process_callback.assert_called_once_with("mock-auth-code")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/context-based-url/foobar"
