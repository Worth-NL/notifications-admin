from enum import Enum
from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user


limiter = Limiter(
    get_remote_address,
    storage_uri=current_app.config("REDIS_URL"),
    default_limits=[current_app.config("DEFAULT_RATE_LIMIT")],
)


class RateLimit(Enum):
    NO_LIMIT = limiter.exempt
    INTERNAL_LIMIT = limiter.limit(current_app.config("INTERNAL_RATE_LIMIT"))
    USER_LIMIT = limiter.limit(current_app.config("USER_RATE_LIMIT"), key_func=lambda: current_user.id)
