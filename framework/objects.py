# Stdlib
import logging
import os

# External Libraries
import quart.flask_patch  # noqa: F401 pylint: disable=unused-import
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Sayonika Internals
from framework.db import db
from framework.mailer import Mailer
from framework.sayonika import Sayonika
from framework.tokens import JWT

__all__ = ("sayonika_instance", "limiter", "logger", "jwt_service", "db", "mailer", "SETTINGS")

sayonika_instance = Sayonika()

SETTINGS = {
    # Default
    "SERVER_BIND": "localhost",
    "SERVER_PORT": 4444,
    "DB_HOST": "localhost",
    "DB_PORT": 5432,
    "DB_USER": "mart",
    "DB_PASS": "Nya",
    "DB_NAME": "sayonika",
    "JWT_SECRET": "testing123"
}

SETTINGS.update({
    k[9:]: v for k, v in os.environ.items()
    if k.startswith("SAYONIKA_")
})

# Use env vars to update config
sayonika_instance.config.update()

limiter = Limiter(
    sayonika_instance,
    key_func=get_remote_address,
    default_limits=SETTINGS.get(
        "RATELIMITS",
        "1 per 2 seconds;20 per minute;1000 per hour"
    ).split(";")
)

logger = logging.getLogger("Sayonika")
logger.setLevel(logging.INFO)

jwt_service = JWT(SETTINGS)

mailer = Mailer()
mailer.init_app(sayonika_instance)
