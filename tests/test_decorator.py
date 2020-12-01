from unittest import mock

import spp_cognito_auth


@mock.patch.object(spp_cognito_auth.Auth, "logged_in")
def test_required_auth_logged_in(mock_logged_in, client):
    mock_logged_in.return_value = True
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"Hello, World!"


@mock.patch.object(spp_cognito_auth.Auth, "logged_in")
def test_required_auth_logged_out(mock_logged_in, auth, client):
    mock_logged_in.return_value = False
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == auth.login_url()
