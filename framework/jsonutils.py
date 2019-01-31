# Stdlib
from datetime import datetime
from enum import Enum

# External Libraries
from quart.json import JSONEncoder


class EnumJsonEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, Enum):
            return o.value

        return super().default(o)


class DateTimeJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


class CombinedEncoder(EnumJsonEncoder, DateTimeJsonEncoder):
    pass
