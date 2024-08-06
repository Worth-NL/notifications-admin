from enum import Enum
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user

from app.config import configs


limiter = Limiter(
    get_remote_address,
    storage_uri=configs.get("REDIS_URL", "memory://"),
    default_limits=["1/minute"],
)


class RateLimit(Enum):
    NO_LIMIT = limiter.exempt
    INTERNAL_LIMIT = limiter.limit("12/minute")
    DEFAULT_USER_LIMIT = limiter.limit("1/minute", key_func=lambda: current_user.id)
    USER_LIMIT = limiter.limit("1/second", key_func=lambda: current_user.id)
