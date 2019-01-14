from quart.exceptions import all_http_exceptions, HTTPException


def abort(status: int, description: str=None, name: str=None) -> None:
    '''
    Polyfill for flask/werkzeug's abort function in quart.
    '''
    err_class = all_http_exceptions.get(status, HTTPException(status, description or 'Unknown', name or 'Unknown'))

    if description is not None:
        err_class.description = description
    if name is not None:
        err_class.name = name

    print(err_class.description)

    raise err_class
