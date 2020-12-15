# SPP Cognito Auth

A python library to easily implement Cognito authentication and authorisation.

A reference usage of this client is provided in <https://github.com/ONSdigital/spp-cognito-poc>

## Installation

### Pip

```sh
pip install git+https://github.com/ONSdigital/spp-cognito-auth.git
```

### Poetry

Add the dependency to your `pyproject.toml`

```toml
[tool.poetry.dependencies]
spp_cognito_auth = { git = "git@github.com:ONSdigital/spp-cognito-auth.git", branch = "main" }
```

## Recommended Cognito group structure

We recommend you set your groups up in the format `<service/purpose>.<team/group>.<permission>`

For example:

- `survey.main.read`
- `survey.main.write`
- `survey.main.manager`
- `survey.secondary.read`
- `survey.secondary.write`
- `other.main.read`

The reason for this recommendation is that you can then use the wildcard role matching made available with `requires_role` or `match_role`.

For example: `survey.*.read` would allow access to a user with either groups `survey.main.read` or `survey.secondary.read`.

Likewise `survey.*.*` would allow access from the any of the `survey` groups above but not the `other` group.

## Using with Flask

Integrating this client with flask is designed to be straightforward.

First, you will want to initialise an auth client and add it to your flask app.

```py
from flask import Flask, session

from spp_cognito_auth import Auth, AuthConfig

application = Flask(__name__)

auth_config = AuthConfig.from_env()
oauth_client = new_oauth_client(auth_config)
application.auth = Auth(auth_config, oauth_client, session)
```

### Adding the auth blueprint

When using cognito it will need to make callbacks to your app to exchange an
authorisation code for an access token. To make this as simple as possible
you can simply import a blueprint

```python
application.register_blueprint(AuthBlueprint().blueprint())
```

The `AuthBlueprint` class takes two optional parameters
(the example below explicitly shows the defaults):

```python
AuthBlueprint(default_url="/", url_prefix="/auth")
```

This would add you routes to your application at `/auth/callback`
and `/auth/logout`. The callback URL is what you would need to configure
in cognito.

### Adding authentication to an endpoint

A simple flask decorator can be used, it will validate authentication and
either redirect a user to login or allow them to access the endpoint.

```python
@application.route("/")
@requires_auth
def home():
    return "Hello, World!"
```

### Adding authorisation to an endpoint

The example below requires authorisation as well as authentication. If a user
attempts to access the endpoint that matches the role `surveys.*.read` they
will be allowed in, otherwise they will receive a `HTTP 403 FORBIDDEN` error.

As this is flask you can add a [custom error handler](https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/)
to serve a custom error page based on the `403` error code.

```python
@application.route("/")
@requires_auth
@requires_role(["surveys.*.read"])
def home():
    return "Hello, World!"
```

### Sessions over 4KB

Most browsers implement a 4KB cookie limit, by default flask stores its session info
in this cookie. During testing we found that users with many roles may cause
issues as there access tokens will exceed this limit.

The workaround for this is to use [Flask-Session](https://flask-session.readthedocs.io/en/latest/)
to store the session information in a backend of your choice and just store a
secure unique reference to the user session on the client side.

**Note**: You must call `flask_session.Session` before initialising `Auth`.

```python
import redis
import os

from flask import Flask, session
from flask_session import Session

from spp_cognito_auth import Auth, AuthConfig

application = Flask(__name__)

store = redis.StrictRedis(host=os.getenv("REDIS_ADDRESS"))
application.config["SESSION_TYPE"] = "redis"
application.config["SESSION_REDIS"] = store
Session(application)

auth_config = AuthConfig.from_env()
oauth_client = new_oauth_client(auth_config)
application.auth = Auth(auth_config, oauth_client, session)
```

### Configuration

Configuration can be set in two ways.

**On the class**:

```python
auth_config = AuthConfig(
    client_id="client-id",
    client_secret="client-secret",
    callback_url="callback-url",
    cognito_domain="cognito_domain",
    cognito_endpoint="cognito-endpoint",
    cognito_scopes=["cognito-scopes"]
)
```

**With environment variables**

```python
auth_config = AuthConfig.from_env()
```

| Setting            | Environment variable | description                                                                                                                                                                                                                                                             |
|--------------------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `client_id`        | `CLIENT_ID`          | The cognito oauth client ID assigned to your app, from teraform this would be something like: `aws_cognito_user_pool_client.client.id`                                                                                                                                  |
| `client_secret`    | `CLIENT_SECRET`      | The cognito oauth client secret assigned to your app, from teraform this would be something like: `aws_cognito_user_pool_client.client.client_secret`                                                                                                                   |
| `callback_url`     | `CALLBACK_URL`       | The callback URL that cognito will use when sending the authorisation code, your app also needs to know this as its part of the validation flow. It will be the URL you deploy this app too, plus `url_prefix` you use on the `AuthBlueprint`, default `/auth/callback` |
| `cognito_domain`   | `COGNITO_DOMAIN`     | The domain you have configured for the cognito hosted UI. This will be `<your_domain>.auth.<aws_region>.amazoncognito.com` a terraform example: `"${aws_cognito_user_pool_domain.cognito.domain}.auth.${var.region}.amazoncognito.com"`                                 |
| `cognito_endpoint` | `COGNITO_ENDPOINT`   | The API endpoint for your cognito service, directly compatible with the terraform attribute `aws_cognito_user_pool.cognito.endpoint`                                                                                                                                    |
| `cognito_scopes`   | `N/A`                | The scopes that you wish to map for auth requests. This is not configurable my an env var but does have a default: `["aws.cognito.signin.user.admin", "email", "openid", "phone", "profile"]`                                                                           |
