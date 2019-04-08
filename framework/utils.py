# External Libraries
import aiohttp
from quart import abort
from sqlalchemy.orm import Query

# Sayonika Internals
from framework.objects import SETTINGS


def paginate(query: Query, page: int, limit: int = 50) -> Query:
    """Paginates a query, calculating the proper offset for the page."""
    return query.limit(limit).offset(page * limit)


async def verify_recaptcha(token: str, session: aiohttp.ClientSession, version: int, action: Optional[str] = None) -> float:
    """Verify a reCAPTCHA request."""

    if version == 2:
        secret = SETTINGS["RECAPTCHA_CHECKBOX_SECRET_KEY"]
    elif version == 3:
        secret = SETTINGS["RECAPTCHA_INVISIBLE_SECRET_KEY"]
    else:
        raise ValueError("Invalid reCAPTCHA version")

    params = {
        "secret": secret,
        "response": token
    }

    async with session.post("https://www.google.com/recaptcha/api/siteverify", params=params) as resp:
        data = await resp.json()

        if data["success"] is False:
            abort(400, "Invalid captcha")

        if version == 3 and action and data["action"] != action:
            abort(400, "Invalid captcha action")

    if version == 3:
        return data["score"]
    else:
        return True


class NamedBytes(bytes):
    """Helper class for having `bytes` with `name` for owo."""

    def __new__(cls, *args, name: str=None, **kwargs):
        inst = bytes.__new__(cls, *args, **kwargs)
        inst.name = name

        return inst
