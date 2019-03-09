# Stdlib
from asyncio import Future
import base64
from datetime import datetime
from functools import partial
import json
from traceback import format_exception

# External Libraries
from Cryptodome.Cipher import AES
from quart import Response, request
from quart.exceptions import WERKZEUG_EXCEPTION_CODES as exception_codes

# Sayonika Internals
from framework.error_handlers.error_common import error_handler
from framework.jsonutils import DatetimeJSONEncoder


def make_auto_future(val):
    fut = Future()
    fut.set_result(val)

    return fut


exception_handlers = {
    code: error_handler(
        # Need to partial the lambda so we can keep the proper code, otherwise it just ends up using the last one (505)
        partial(
            lambda x, err: make_auto_future(Response(err.description, x)),
            code
        )
    )
    for code in exception_codes
}

# Custom 429 message
exception_handlers[429] = error_handler(
    lambda err: make_auto_future(Response(f"Ratelimit for this endpoint: {err.description}", 429))
)


@error_handler
async def handle_500(err):
    from framework.objects import SETTINGS, jwt_service

    tb = ''.join(
        format_exception(type(err), err, err.__traceback__)
    )
    token = request.headers.get("Authorization", request.cookies.get("token"))
    parsed = await jwt_service.verify_login_token(token, True)

    if not parsed:
        meta = {}
    else:
        meta = {
            "id": parsed["id"]
        }

    meta["time"] = datetime.utcnow()

    # Send traceback and metadata in base64 and encrypted.
    data = json.dumps({
        "tb": tb,
        "d": meta
    }, cls=DatetimeJSONEncoder).encode()

    c = AES.new(SETTINGS["AES_KEY"], AES.MODE_CTR)
    digest = base64.encodebytes(c.encrypt(data))
    nonce = base64.b64encode(c.nonce)

    res = nonce + b"." + digest

    # TODO: Sentry error reporting integration

    return Response(res.decode(), 500)


exception_handlers[500] = handle_500
