# Stdlib
import logging
import os

# External Libraries
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from gino import Gino
from sqlalchemy.engine.url import URL

# Sayonika Internals
from framework.authentication import Authenticator
from framework.tokens import JWT
from framework.sayonika import Sayonika

__all__ = ("sayonika_instance", "limiter", "logger", "auth_service", "jwt_service", "db", "SETTINGS")

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

auth_service = Authenticator(SETTINGS)
jwt_service = JWT(SETTINGS)

db = Gino(URL("psycopg2", username=SETTINGS["DB_NAME"], password=SETTINGS["DB_PASS"],
              host=SETTINGS["DB_HOST"], port=SETTINGS["DB_PORT"], database=SETTINGS["DB_NAME"]))
