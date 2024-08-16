from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user


class RateLimit:
    NO_LIMIT = None
    INTERNAL_LIMIT = None
    USER_LIMIT = None

    @classmethod
    def init(cls, app):
        global limiter

        limiter = Limiter(
            get_remote_address,
            storage_uri=app.config.get("REDIS_URL") if app.config.get("REDIS_ENABLED") else "memory://",
            default_limits=[app.config.get("DEFAULT_RATE_LIMIT")],
            key_prefix="limit-",
        )

        cls.NO_LIMIT = limiter.exempt
        cls.INTERNAL_LIMIT = limiter.limit(app.config.get("INTERNAL_RATE_LIMIT"))
        cls.USER_LIMIT = limiter.limit(app.config.get("USER_RATE_LIMIT"), key_func=lambda: current_user.id)

        limiter.init_app(app)


def init_limiters(app):
    RateLimit.init(app)
