"""
Custom key function for flask-limiter.
Probably needs to be in its own file due to Quart's flask patching.
(We should probably port limiter to Quart properly (or just wait for FastAPI rewrite lol))
"""
# External Libraries
from flask import request


def get_ratelimit_key():
    token = request.headers.get("Authorization", request.cookies.get("token"))

    if token:
        return token
    if request.access_route:
        return request.access_route[0]
    return request.remote_addr
