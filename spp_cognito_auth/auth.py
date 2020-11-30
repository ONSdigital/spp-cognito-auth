from typing import Any
from urllib.parse import urlparse

from authlib.integrations.requests_client import OAuth2Session

from .config import AuthConfig
from .utils import fix_url


class Auth:
    def __init__(self, config: AuthConfig, oauth: OAuth2Session, session: Any) -> None:
        self._config = config
        self._session = session
        self._oauth = oauth

    def login_url(self) -> str:
        return (
            f"{fix_url(self._config.cognito_domain)}/login?"
            + f"client_id={self._config.client_id}&"
            + "response_type=code&"
            + f"scope={'+'.join(self._config.cognito_scopes)}&"
            + f"redirect_uri={self._config.callback_url}"
        )

    def public_key_url(self) -> str:
        return f"{fix_url(self._config.cognito_endpoint)}/.well-known/jwks.json"

    def token_url(self) -> str:
        return f"{fix_url(self._config.cognito_domain)}/oauth2/token"
