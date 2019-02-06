# Stdlib
import json

# External Libraries
from marshmallow.fields import Field
import quart
from quart.exceptions import HTTPException
from webargs import core
from webargs.asyncparser import AsyncParser


def abort(http_status_code, exc=None, **kwargs):
    try:
        quart.abort(http_status_code)
    except HTTPException as err:
        err.description = json.dumps(kwargs.get("messages"))
        err.data = kwargs
        err.exc = exc

        raise err


def is_json_request(req: quart.Request):
    return core.is_json(req.mimetype)


class QuartParser(AsyncParser):
    """Quart request argument parser"""

    __location_map__ = dict(view_args="parse_view_args", **core.Parser.__location_map__)

    def parse_view_args(self, req: quart.Request, name: str, field: Field):
        """Pull a value from the request's ``view_args``."""
        return core.get_value(req.view_args, name, field)

    async def parse_json(self, req: quart.Request, name: str, field: Field):
        """Pull a json value from the request."""
        data = self._cache.get("json")

        if data is None:
            if not is_json_request(req):
                return core.missing

            data = await req.get_data(False)

            try:
                self._cache["json"] = data = core.parse_json(data)
            except json.JSONDecodeError as err:
                if err.doc == "":
                    return core.missing

                return self.handle_invalid_json_error(err, req)

        return core.get_value(data, name, field, allow_many_nested=True)

    def parse_querystring(self, req: quart.Request, name: str, field: Field):
        """Pull a querystring value from the request."""
        return core.get_value(req.args, name, field)

    async def parse_form(self, req: quart.Request, name: str, field: Field):
        """Pull a form value from the request."""
        try:
            return core.get_value(await req.form, name, field)
        except AttributeError:
            pass

        return core.missing

    def parse_headers(self, req: quart.Request, name: str, field: Field):
        """Pull a value from the header data."""
        return core.get_value(req.headers, name, field)

    def parse_cookies(self, req: quart.Request, name: str, field: Field):
        """Pull a value from the cookiejar."""
        return core.get_value(req.cookies, name, field)

    async def parse_files(self, req: quart.Request, name: str, field: Field):
        """Pull a file from the request."""
        return core.get_value(await req.files, name, field)

    def handle_error(self, error, req, schema, error_status_code, error_headers):
        """
        Handles errors during parsing.
        Aborts the current HTTP request and responds with a 422 error.
        """
        status_code = error_status_code or self.DEFAULT_VALIDATION_STATUS
        abort(
            status_code,
            exc=error,
            messages=error.messages,
            schema=schema,
            headers=error_headers,
        )

    def handle_invalid_json_error(self, error, req, *args, **kwargs):  # pylint: disable=unused-argument
        abort(400, exc=error, messages={"json": ["Invalid JSON body."]})

    def get_default_request(self):
        """Override to use Flask's thread-local request objec by default"""
        return quart.request


parser = QuartParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
