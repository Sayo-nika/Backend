# Stdlib
import asyncio
import logging

# External Libraries
import quart.flask_patch  # noqa: F401 pylint: disable=unused-import
from aioredis import ConnectionsPool
from flask_limiter import Limiter
from quart_cors import cors

# Sayonika Internals
from framework.db import db
from framework.init_later_redis import InitLaterRedis
from framework.limiter import get_ratelimit_key
from framework.mailer import Mailer
from framework.sayonika import Sayonika
from framework.settings import SETTINGS
from framework.tokens import JWT

__all__ = ("sayonika_instance", "limiter", "logger", "jwt_service", "db", "mailer", "loop", "redis")

loop = asyncio.get_event_loop()

logger = logging.getLogger("Sayonika")
sayonika_instance = cors(
    Sayonika(),
    allow_origin=["https://sayonika.moe",
                  "*"]  # Remove this one when ready for prod
)
jwt_service = JWT(SETTINGS)
mailer = Mailer(SETTINGS)
limiter = Limiter(
    key_func=get_ratelimit_key,
    default_limits=SETTINGS.get(
        "RATELIMITS",
        "5 per 2 seconds;1000 per hour"
    ).split(";")
)
redis = InitLaterRedis(
    ConnectionsPool(SETTINGS["REDIS_URL"], minsize=5, maxsize=10, loop=loop)
)

# Use env vars to update config
sayonika_instance.config.update(SETTINGS)
limiter.init_app(sayonika_instance)
logger.setLevel(logging.INFO)
