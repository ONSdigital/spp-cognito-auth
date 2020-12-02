from datetime import datetime, timedelta
from typing import Any, List

import requests
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.jose.errors import ExpiredTokenError
from authlib.oauth2.rfc6749 import OAuth2Token
from cachecontrol import CacheController

from .config import AuthConfig
from .utils import fix_url


class Auth:
    def __init__(self, config: AuthConfig, oauth: OAuth2Session, session: Any) -> None:
        self._config = config
        self._session = session
        self._oauth = oauth
        self._jwks_expires_at = None
        self._jwks_token = None

    def login_url(self) -> str:
        return self._cognito_url("login")

    def logout_url(self) -> str:
        return self._cognito_url("logout")

    def public_key_url(self) -> str:
        return f"{fix_url(self._config.cognito_endpoint)}/.well-known/jwks.json"

    def token_url(self) -> str:
        return f"{fix_url(self._config.cognito_domain)}/oauth2/token"

    def process_callback(self, auth_code: str) -> None:
        auth_info = self.get_auth_token(auth_code)
        self._session["access_token"] = auth_info["access_token"]
        self._session["id_token"] = auth_info["id_token"]
        self._session["refresh_token"] = auth_info["refresh_token"]
        self._session["expires_at"] = auth_info["expires_at"]

        token = jwt.decode(self._session["access_token"], self.get_public_keys())
        self._session["username"] = token["username"]
        self._session["roles"] = token["cognito:groups"]

    def logged_in(self) -> bool:
        if "access_token" in self._session:
            try:
                token = jwt.decode(
                    self._session["access_token"], self.get_public_keys()
                )
                token.validate()
                return True
            except ExpiredTokenError:
                pass
        return False

    def logout(self) -> None:
        self._session.clear()

    def get_auth_token(self, auth_code: str) -> OAuth2Token:
        return self._oauth.fetch_token(
            self.token_url(),
            grant_type="authorization_code",
            code=auth_code,
            authorization_response=self._config.callback_url,
        )

    def get_public_keys(self) -> str:
        if (
            self._jwks_token is None
            or self._jwks_expires_at is None
            or self._jwks_expires_at <= datetime.now()
        ):
            resp = requests.get(self.public_key_url())
            cache_control = CacheController().parse_cache_control(resp.headers)
            max_age = cache_control.get("max-age", 0)
            self._jwks_expires_at = datetime.now() + timedelta(
                seconds=float(max_age)
            )  # type: ignore
            self._jwks_token = resp.json()
        return self._jwks_token  # type: ignore

    def get_username(self) -> str:
        return self._session.get("username")

    def get_roles(self) -> List[str]:
        return self._session.get("roles", [])

    def match_role(self, role_matcher: str) -> bool:
        role_matcher = role_matcher.split(".")
        for role in self.get_roles():
            split_role = role.split(".")
            role_matched = []
            for index, role_part in enumerate(role_matcher):
                if role_part == "*":
                    role_matched.append(True)
                    continue
                role_matched.append(role_part == split_role[index])
            if all(role_matched):
                return True
        return False

    def set_redirect(self, url: str) -> None:
        self._session["redirect_url"] = url

    def get_redirect(self) -> str:
        return self._session.get("redirect_url")

    def _cognito_url(self, path: str) -> str:
        return (
            f"{fix_url(self._config.cognito_domain)}/{path}?"
            + f"client_id={self._config.client_id}&"
            + "response_type=code&"
            + f"scope={'+'.join(self._config.cognito_scopes)}&"
            + f"redirect_uri={self._config.callback_url}"
        )
