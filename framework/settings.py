# Stdlib
import os

__all__ = ("SETTINGS",)

SETTINGS = {
    # Default
    "SERVER_BIND": "0.0.0.0",
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
