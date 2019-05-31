# Stdlib
from datetime import datetime, timedelta
from enum import Enum

# External Libraries
from quart.json import JSONEncoder


class EnumJSONEncoder(JSONEncoder):
    """JSON encoder for encoding enum values."""
    def default(self, o):
        if isinstance(o, Enum):
            return o.value

        return super().default(o)


class DatetimeJSONEncoder(JSONEncoder):
    """JSON encoder for encoding datetime objects."""
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


class TimedeltaJSONEncoder(JSONEncoder):
    """JSON encoder for encoding timedelta objects."""
    def default(self, o):
        if isinstance(o, timedelta):
            return round(o.total_seconds() * 1000)

        return super().default(o)


class CombinedEncoder(EnumJSONEncoder, DatetimeJSONEncoder, TimedeltaJSONEncoder):
    """JSON encoder that inherits functionality of other custom encoders."""
