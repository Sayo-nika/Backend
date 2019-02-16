from asyncio import Future
from functools import partial

# External Libraries
from quart import Response
from quart.exceptions import WERKZEUG_EXCEPTION_CODES as exception_codes

# Sayonika Internals
from framework.error_handlers.error_common import error_handler


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

exception_handlers[429] = error_handler(
    lambda err: make_auto_future(Response(f"Ratelimit for this endpoint: {err.description}", 429))
)
