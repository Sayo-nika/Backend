# Stdlib
from functools import wraps
import json as _json

# External Libraries
from flask import Response, abort

# Sayonika Internals
from framework.objects import limiter, auth_service

__all__ = ("json", "auth_has_ratelimit", "auth_only")


def json(func):
    """
    Wraps a function to return a unified JSON format
    """
    @wraps(func)
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        text = response.response[0].decode()
        try:
            data = _json.loads(text)
        except _json.JSONDecodeError:
            data = text

        result = _json.dumps({
            "result": data,
            "status": response._status_code,  # flake8: noqa pylint: disable=protected-access
            "success": True if 200 <= response._status_code < 300 else False  # flake8: noqa pylint: disable=protected-access
        })

        return Response(
            response=result,
            headers=response.headers,
            status=response.status,
            content_type="application/json"
        )

    return inner


def requires_keycloak_login(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if auth_service.has_authorized_access(*args, **kwargs):
            return func(*args, **kwargs)
        return abort(403)

    return inner


def requires_keycloak_admin(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if auth_service.has_admin_access(*args, **kwargs):
            return func(*args, **kwargs)
        return abort(403)

    return inner
