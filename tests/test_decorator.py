from unittest import mock

import spp_cognito_auth


@mock.patch.object(spp_cognito_auth.Auth, "logged_in")
def test_required_auth_logged_in(mock_logged_in, client):
    mock_logged_in.return_value = True
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"Hello, World!"


@mock.patch.object(spp_cognito_auth.Auth, "logged_in")
def test_required_auth_logged_out(mock_logged_in, client, flask_app):
    mock_logged_in.return_value = False
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == flask_app.auth.login_url()
    assert flask_app.auth.get_redirect() == "http://localhost/"


@mock.patch.object(spp_cognito_auth.Auth, "logged_in")
@mock.patch.object(spp_cognito_auth.Auth, "match_role")
def test_required_roles_authorised(mock_match_role, mock_logged_in, client):
    mock_match_role.return_value = True
    mock_logged_in.return_value = True
    response = client.get("/test-roles")
    assert response.status_code == 200
    assert response.data == b"Welcome to the Role endpoint!"


@mock.patch.object(spp_cognito_auth.Auth, "logged_in")
@mock.patch.object(spp_cognito_auth.Auth, "match_role")
def test_required_roles_not_authorised(mock_match_role, mock_logged_in, client):
    mock_match_role.return_value = False
    mock_logged_in.return_value = True
    response = client.get("/test-roles")
    assert response.status_code == 403
