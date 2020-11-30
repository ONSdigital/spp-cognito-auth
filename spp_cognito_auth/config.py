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
