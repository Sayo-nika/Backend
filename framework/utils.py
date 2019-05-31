# Stdlib
import hashlib
import string
from typing import Optional
import urllib.parse as urlp

# External Libraries
import aiohttp
from quart import abort
from sqlalchemy.orm import Query
from unidecode import unidecode

# Sayonika Internals
from framework.objects import SETTINGS

GRAVATAR_BASE = "https://www.gravatar.com/avatar/{}?s=512"  # noqa: P103
DEFAULT_AVATAR = GRAVATAR_BASE.format(
    hashlib.md5(b"hello@sayonika.moe").hexdigest()  # noqa: S303
)


def generalize_text(text: str) -> str:
    """
    Transforms a given string into a lowercased, dash separated sequence,
    with non-ascii characters and punctuation removed.

    e.g.
    Input: öBLiq.ue fońt]
    Output: oblique-font
    """
    return (
        # Rejoin with only one space
        " ".join(
            # Remove unicode characters by trying to find visually similar ASCII
            unidecode(text)
            # Strip punctuation characters
            .translate(str.maketrans("", "", string.punctuation))
            # Split on any whitespace character, including multiple
            .split()
        )
        .strip()
        .replace(" ", "-")
        .lower()
    )


def generate_gravatar(email: str) -> str:
    """Generates a Gravatar URL given an email. Comes with default fallback."""
    email_ = email.strip().lower()
    hash_ = hashlib.md5(email_.encode()).hexdigest()  # noqa: S303

    return GRAVATAR_BASE.format(hash_) + f"&d={urlp.quote(DEFAULT_AVATAR, '')}"


def paginate(query: Query, page: int, limit: int = 50) -> Query:
    """Paginates a query, calculating the proper offset for the page."""
    return query.limit(limit).offset(page * limit)


async def verify_recaptcha(token: str, session: aiohttp.ClientSession, version: int, action: Optional[str] = None
                           ) -> float:
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
    return True


class NamedBytes(bytes):
    """Helper class for having `bytes` with `name` for owo."""

    def __new__(cls, *args, name: str = None, **kwargs):
        inst = bytes.__new__(cls, *args, **kwargs)
        inst.name = name

        return inst
