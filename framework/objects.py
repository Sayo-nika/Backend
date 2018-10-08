# Stdlib
import logging

# External Libraries
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Sayonika Internals
from framework.authentication import Authenticator
from framework.jsonfile import JsonFile
from framework.sayonika import Sayonika

__all__ = ("sayonika_instance", "limiter", "logger", "auth_service", "mods_json")

sayonika_instance = Sayonika()

limiter = Limiter(
    sayonika_instance,
    key_func=get_remote_address,
    default_limits=["1 per 2 seconds", "20 per minute", "1000 per hour"]
)

logger = logging.getLogger("Sayonika")
logger.setLevel(logging.INFO)

auth_service = Authenticator("resources/json/keys.json")
auth_service.reload_tokens()

mods_json = JsonFile("mods/mods.json")
