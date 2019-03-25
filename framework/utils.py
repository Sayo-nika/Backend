# External Libraries
import aiohttp
from quart import abort
from sqlalchemy.orm import Query

# Sayonika Internals
from framework.objects import SETTINGS


def paginate(query: Query, page: int, limit: int = 50) -> Query:
    """Paginates a query, calculating the proper offset for the page."""
    return query.limit(limit).offset(page * limit)


async def verify_recaptcha(token: str, action: str, session: aiohttp.ClientSession) -> float:
    """Verify an 'invisible' reCAPTCHA request."""
    params = {
        "secret": SETTINGS["RECAPTCHA_INVISIBLE_SECRET_KEY"],
        "response": token
    }

    async with session.post("https://www.google.com/recaptcha/api/siteverify", params=params) as resp:
        data = await resp.json()

        if data["success"] is False:
            abort(400, "Invalid captcha")

        if data["action"] != action:
            abort(400, "Invalid captcha action")

    return data["score"]


class NamedBytes(bytes):
    """Helper class for having `bytes` with `name` for owo."""

    def __new__(cls, *args, name: str=None, **kwargs):
        inst = bytes.__new__(cls, *args, **kwargs)
        inst.name = name

        return inst
