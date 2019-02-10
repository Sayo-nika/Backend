# Stdlib
from datetime import datetime, timedelta
from enum import Enum

# External Libraries
from quart.json import JSONEncoder


class EnumJSONEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, Enum):
            return o.value

        return super().default(o)


class DatetimeJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


class TimedletaJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, timedelta):
            return round(o.total_seconds() * 1000)

        return super().default(o)


class CombinedEncoder(EnumJSONEncoder, DatetimeJSONEncoder, TimedletaJSONEncoder):
    pass
