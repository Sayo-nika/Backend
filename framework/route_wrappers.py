# Stdlib
from functools import wraps
import json as _json

# External Libraries
from quart import Response, abort, request

# Sayonika Internals
from framework.authentication import Authenticator

__all__ = ("json", "requires_login", "requires_admin")


def json(func):
    """Wraps a route to return a preformatted JSON format with other response details."""

    @wraps(func)
    async def inner(*args, **kwargs):
        response = await func(*args, **kwargs)
        text = await response.get_data(False)

        try:
            data = _json.loads(text)
        except _json.JSONDecodeError:
            data = text

        result = _json.dumps({
            "result": data,
            "status": response.status_code,
            "success": response.status_code < 400
        }, indent=4 if request.args.get("pretty") == "true" else None)

        return Response(
            response=result,
            headers=response.headers,
            status=response.status_code,
            content_type="application/json"
        )

    return inner


def requires_login(func):
    """Makes a route require login to access."""

    @wraps(func)
    async def inner(*args, **kwargs):
        if await Authenticator.has_authorized_access(*args, **kwargs):
            return await func(*args, **kwargs)
        return abort(403)

    return inner


def requires_admin(func):
    """Makes a route require a user to be an admin to access."""

    @wraps(func)
    async def inner(*args, **kwargs):
        if await Authenticator.has_admin_access():
            return await func(*args, **kwargs)
        return abort(403)

    return inner


def requires_supporter(func):
    """Makes a route require a user to be a supporter to access."""

    @wraps(func)
    async def inner(*args, **kwargs):
        if await Authenticator.has_supporter_features():
            return await func(*args, **kwargs)
        return abort(403)

    return inner
