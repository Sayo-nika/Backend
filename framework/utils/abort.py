# External Libraries
from quart import Response


def abort(status: int, description: str = None) -> None:
    '''
    Polyfill for flask/werkzeug's abort function in quart.
    '''
    return Response(
        response=description,
        status=status,
        content_type="application/json"
    )
