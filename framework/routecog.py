# Stdlib
import inspect

# Sayonika Internals
from framework.objects import logger
from framework.route import Route
from framework.sayonika import Sayonika

__all__ = ("RouteCog",)


class RouteCog:
    """Manages multiple routes together to be registered all at the same time."""

    def __init__(self, core: Sayonika):
        self.core = core
        self.logger = logger

    def register(self):
        """Registers all routes on a Sayonika instance."""
        for _, member in inspect.getmembers(self):
            if isinstance(member, Route):
                member.set_parent(self)
                member.register(self.core)
