import os
from dataclasses import dataclass, field
from typing import List

DEFAULT_SCOPES = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "phone",
    "profile",
]


@dataclass
class AuthConfig:
    client_id: str
    client_secret: str
    callback_url: str
    cognito_domain: str
    cognito_endpoint: str
    cognito_scopes: List[str] = field(default_factory=lambda: DEFAULT_SCOPES)

    @classmethod
    def from_env(cls) -> "AuthConfig":
        return cls(
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            callback_url=os.environ["CALLBACK_URL"],
            cognito_domain=os.environ["COGNITO_DOMAIN"],
            cognito_endpoint=os.environ["COGNITO_ENDPOINT"]
        )