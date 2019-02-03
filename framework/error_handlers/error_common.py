# Stdlib
import json

# External Libraries
from quart import Response, request


# Moved out of response_wrappers.py due to circular imports
def error_handler(func):
    """
    Similar to `json`, but a different format
    """

    async def inner(*args, **kwargs):
        response = await func(*args, **kwargs)
        text = await response.get_data(False)

        try:
            text = json.loads(text)
        except Exception:
            pass

        result = json.dumps({
            "error": text,
            "status": response.status_code,
            "success": True if 200 <= response.status_code < 300 else False
        }, indent=4 if request.args.get("pretty") == "true" else None)

        return Response(
            response=result,
            headers=response.headers,
            status=response.status_code,
            content_type="application/json"
        )

    return inner
