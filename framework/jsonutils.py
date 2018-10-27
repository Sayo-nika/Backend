# Stdlib

from enum import Enum

# External Libraries

from flask.json import JSONEncoder


class EnumJsonEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, Enum):
            return o.value
        return JSONEncoder.default(self, o)
