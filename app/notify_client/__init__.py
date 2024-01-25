from flask import g, has_request_context, request
from flask_login import current_user
from notifications_python_client import __version__
from notifications_python_client.base import BaseAPIClient
from notifications_utils.clients.redis import RequestCache

from app.extensions import redis_client

cache = RequestCache(redis_client)


def _attach_current_user(data):
    return dict(created_by=current_user.id, **data)


class NotifyAdminAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__("a" * 73, "b")

    def init_app(self, app):
        self.base_url = app.config["API_HOST_NAME"]
        self.service_id = app.config["ADMIN_CLIENT_USER_NAME"]
        self.api_key = app.config["ADMIN_CLIENT_SECRET"]
        self.route_secret = app.config["ROUTE_SECRET_KEY_1"]

    def generate_headers(self, api_token):
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {api_token}",
            "X-Custom-Forwarder": self.route_secret,
            "User-agent": f"NOTIFY-API-PYTHON-CLIENT/{__version__}",
        }
        if has_request_context():
            if hasattr(request, "get_onwards_request_headers"):
                headers = {
                    **request.get_onwards_request_headers(),
                    **headers,
                }
            if g.user_id:
                headers["X-Notify-User-Id"] = g.user_id

        return headers


class InviteTokenError(Exception):
    pass
