# Stdlib
import glob
import importlib
from os.path import sep

# External Libraries
from aiohttp import ClientSession, DummyCookieJar
from quart import Quart

# Sayonika Internals
from framework.error_handlers.error_handlers import exception_handlers
from framework.jsonutils import CombinedEncoder

__all__ = ("Sayonika",)


class Sayonika(Quart):
    """
    Core application. Wraps Flask to use `super.run` with some default arguments,
    while the user only has to run `run` without providing additional arguments.
    Additionally, we use this class to pass around to register all routes
    """

    def __init__(self):
        super().__init__("Sayonika")

        self.route_dir = ""
        self.json_encoder = CombinedEncoder
        self.aioh_sess = ClientSession(cookie_jar=DummyCookieJar(), raise_for_status=True)

        for code, func in exception_handlers.items():
            self.register_error_handler(code, func)

    def gather(self, route_dir: str):
        """Gathers and registers all routes in a specified directory."""
        for path in glob.glob(f"{route_dir}/**.py"):
            module = importlib.import_module(path.replace(sep, ".")[:-3])

            if not hasattr(module, "setup"):
                raise ValueError(
                    f"Module {repr(module.__name__)} does not have a `setup` function!"
                )

            module.setup(self)
            del module

    # pylint: disable=keyword-arg-before-vararg
    def run(self, host: str = "localhost", port: int = 4444, *args, **kwargs):
        super().run(host, port, *args, **kwargs)
