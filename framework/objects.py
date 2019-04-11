# Stdlib
import asyncio
import logging
import os

# External Libraries
import quart.flask_patch  # noqa: F401 pylint: disable=unused-import
from aioredis import ConnectionsPool
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from owo import Client as OWOClient

# Sayonika Internals
from framework.db import db
from framework.init_later_redis import InitLaterRedis
from framework.mailer import Mailer
from framework.sayonika import Sayonika
from framework.tokens import JWT

__all__ = ("sayonika_instance", "limiter", "logger", "jwt_service", "db", "mailer", "SETTINGS", "loop", "redis", "owo")

loop = asyncio.get_event_loop()
SETTINGS = {
    # Default
    "SERVER_BIND": "localhost",
    "SERVER_PORT": 4444,
    "DB_HOST": "localhost",
    "DB_PORT": 5432,
    "DB_USER": "sayonika",
    "DB_PASS": "sayonika",
    "DB_NAME": "sayonika",
    "JWT_SECRET": "testing123",
    "AES_KEY": "this is a  pretty long key oh no",
    "REDIS_URL": "redis://localhost:6379/0",
    "EMAIL_BASE": "http://localhost:4444",
    "MEDIUM_PUBLICATION": "sayonika"
}

SETTINGS.update({
    k[9:]: v for k, v in os.environ.items()
    if k.startswith("SAYONIKA_")
})

if len(SETTINGS["AES_KEY"]) != 32:
    # Early catch for wrong length key
    raise ValueError("SAYONIKA_AES_KEY must be a 32 bit key.")
else:
    SETTINGS["AES_KEY"] = SETTINGS["AES_KEY"].encode()

logger = logging.getLogger("Sayonika")
sayonika_instance = Sayonika()
jwt_service = JWT(SETTINGS)
mailer = Mailer()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=SETTINGS.get(
        "RATELIMITS",
        "1 per 2 seconds;20 per minute;1000 per hour"
    ).split(";")
)
redis = InitLaterRedis(
    ConnectionsPool(SETTINGS["REDIS_URL"], minsize=5, maxsize=10, loop=loop)
)
owo = OWOClient(SETTINGS["OWO_KEY"])

# Use env vars to update config
sayonika_instance.config.update(SETTINGS)
limiter.init_app(sayonika_instance)
mailer.init_app(sayonika_instance)
logger.setLevel(logging.INFO)
