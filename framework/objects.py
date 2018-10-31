# Stdlib
import logging
import os

# External Libraries
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Sayonika Internals
from framework.authentication import Authenticator
from framework.database import DBHandler
from framework.sayonika import Sayonika

__all__ = ("sayonika_instance", "limiter", "logger", "auth_service", "database_handle")

sayonika_instance = Sayonika()

SETTINGS = {
    # Default
    "DB_HOST": "localhost",
    "DB_PORT": 5432,
    "DB_USER": "mart",
    "DB_PASS": "Nya",
    "DB_NAME": "sayonika"
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

database_handle = DBHandler(user=SETTINGS["DB_USER"], password=SETTINGS["DB_PASS"],
                            database=SETTINGS["DB_NAME"], host=SETTINGS["DB_HOST"],
                            port=SETTINGS["DB_PORT"])
