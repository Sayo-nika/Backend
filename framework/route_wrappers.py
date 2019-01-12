# Stdlib
from functools import wraps
import json as _json

# External Libraries
from quart import Response, abort, request

# Sayonika Internals
from framework.authentication import Authenticator

__all__ = ("json", "requires_login", "requires_admin")


def json(func):
    """
    Wraps a function to return a unified JSON format
    """

    @wraps(func)
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        text = response.response[0]

        # Mitigate an issue where `response.response[0]` is a string on Windows, and a `bytes` on Linux.
        # God know's why they're different.
        if type(text) is bytes:
            text = text.decode()

        try:
            data = _json.loads(text)
        except _json.JSONDecodeError:
            data = text

        result = _json.dumps({
            "result": data,
            "status": response._status_code,  # flake8: noqa pylint: disable=protected-access
            "success": True if 200 <= response._status_code < 300 else False  # flake8: noqa pylint: disable=protected-access
        }, indent=4 if request.args.get("pretty") == "true" else None)

        return Response(
            response=result,
            headers=response.headers,
            status=response.status,
            content_type="application/json"
        )

    return inner


def requires_login(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        if await Authenticator.has_authorized_access(*args, **kwargs):
            return func(*args, **kwargs)
        return abort(403)

    return inner


def requires_admin(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        if await Authenticator.has_admin_access():
            return func(*args, **kwargs)
        return abort(403)

    return inner

def requires_supporter(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        if await Authenticator.has_supporter_features():
            return func(*args, **kwargs)
        return abort(403)
