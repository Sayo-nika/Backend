# Stdlib
import hashlib
import mimetypes
import string
from typing import Optional
import urllib.parse as urlp

# External Libraries
import aiohttp
from quart import abort, request
from sqlalchemy.orm import Query
from unidecode import unidecode

# Sayonika Internals
from framework.objects import SETTINGS, jwt_service

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


async def verify_recaptcha(token: str, session: aiohttp.ClientSession, action: Optional[str] = None
                           ) -> float:
    """Verify a reCAPTCHA request."""

    secret = SETTINGS["RECAPTCHA_SECRET_KEY"]

    params = {
        "secret": secret,
        "response": token
    }

    async with session.post("https://www.google.com/recaptcha/api/siteverify", params=params) as resp:
        data = await resp.json()

        if data["success"] is False:
            abort(400, "Invalid captcha")

        if data["action"] != action:
            abort(400, "Invalid captcha action")

    return data["score"]


async def get_token_user() -> str:
    token = request.headers.get("Authorization", request.cookies.get("token"))
    parsed_token = await jwt_service.verify_login_token(token, True)

    return parsed_token["id"] if isinstance(parsed_token, dict) else None


async def ipfs_upload(file: bytes, filename: str, session: aiohttp.ClientSession) -> dict:
    form = aiohttp.FormData()
    form.add_field("file", file, filename=filename, content_type=mimetypes.guess_type(filename)[0])

    async with session.post("https://ipfs.infura.io:5001/api/v0/add") as resp:
        data = await resp.json()

    return data
