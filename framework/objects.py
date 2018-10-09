# Stdlib
import logging
import os

# External Libraries
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Sayonika Internals
from framework.authentication import Authenticator
from framework.jsonfile import JsonFile
from framework.sayonika import Sayonika

__all__ = ("sayonika_instance", "limiter", "logger", "auth_service", "mods_json")

sayonika_instance = Sayonika()

# Use env vars to update config
sayonika_instance.config.update({k[9:]: v  # Strip 'SAYONIKA_'
                                 for k, v in os.environ.items()
                                 if k.startswith("SAYONIKA_")})

limiter = Limiter(
    sayonika_instance,
    key_func=get_remote_address,
    default_limits=["1 per 2 seconds", "20 per minute", "1000 per hour"]
)

logger = logging.getLogger("Sayonika")
logger.setLevel(logging.INFO)

auth_service = Authenticator("settings.json")

mods_json = JsonFile("mods/mods.json")
