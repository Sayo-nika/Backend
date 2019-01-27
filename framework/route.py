# Stdlib
import functools

# External Libraries
from quart import request

# Sayonika Internals
from framework.sayonika import Sayonika

__all__ = ("route", "Route", "multiroute")


def route(path, **kwargs):
    """
    Wraps a function to turn it into a `Route`.
    """

    def decorator(func):
        return Route(func, path, **kwargs)

    return decorator


routes = {}


def multiroute(path, methods=["GET"], other_methods=[]):
    if path not in routes:
        routes[path] = {"methods": methods + other_methods}

    def f(func):
        for method in methods:
            routes[path][method] = func

        @functools.wraps(func)
        def switch(*args, **kwargs):
            return routes[path][request.method](*args, **kwargs)

        if all(key in routes[path] for key in routes[path]["methods"]):
            return Route(switch, path, methods=routes[path]["methods"])
        return

    return f


class Route:
    """
    Route class wrapper to register them on the application
    """

    def __init__(self, func, path: str, **kwargs):
        self.func = func
        self.path = path
        self.kwargs = kwargs
        self.parent = None
        self.kwargs['strict_slashes'] = False  # Don't care about dangling / on routes.

    def register(self, core: Sayonika):
        func = functools.partial(self.func, self.parent)
        core.add_url_rule(self.path, self.func.__name__, func, **self.kwargs)

    def set_parent(self, parent):
        self.parent = parent
