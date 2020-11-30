class TestAuth:
    def test_login_url(self, auth):
        assert auth.login_url() == (
            "https://test-cognito-domain.test.com/login?"
            + "client_id=test-client-id&"
            + "response_type=code&"
            + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
            + f"redirect_uri=http://test-app-host.test.com/auth/callback"
        )

    def test_public_key_url(self, auth):
        assert (
            auth.public_key_url()
            == "https://test-cognito-endpoint.test.com/.well-known/jwks.json"
        )

    def test_token_url(self, auth):
        assert auth.token_url() == "https://test-cognito-domain.test.com/oauth2/token"
