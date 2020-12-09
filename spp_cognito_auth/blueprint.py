from collections import Callable

from flask import Blueprint, current_app, redirect, request
from werkzeug.wrappers import Response


class AuthBlueprint:
    def __init__(self, default_url: str = "/", url_prefix: str = "/auth") -> None:
        self.default_url = default_url
        self.url_prefix = url_prefix
        self.auth_blueprint = Blueprint(
            name="auth", import_name=__name__, url_prefix=self.url_prefix
        )

    def blueprint(self) -> Blueprint:
        self.add_route("/callback", self.callback)
        self.add_route("/logout", self.logout)
        return self.auth_blueprint

    def add_route(self, route: str, view_func: Callable) -> None:
        self.auth_blueprint.add_url_rule(route, view_func.__name__, view_func)

    def callback(self) -> Response:
        auth_code = request.args.get("code")
        state = request.args.get("state")
        if not current_app.auth.validate_state(state):
            return self.logout()
        current_app.auth.process_callback(auth_code)
        redirect_url = current_app.auth.get_redirect()
        if redirect_url:
            return redirect(redirect_url)
        return redirect(self.default_url)

    def logout(self) -> Response:
        current_app.auth.logout()
        return redirect(current_app.auth.logout_url())
