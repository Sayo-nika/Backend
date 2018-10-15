from enum import Enum

from pony.orm.dbapiprovider import Converter
from pony.orm.dbproviders.postgres import PGProvider as PGProvider_
from pony.utils import throw


class EnumConverter(Converter):
    type_: type

    def init(self, kwargs):
        super().init(kwargs)
        self.type_ = self.attr.py_type
        print(self.type_)

    def validate(self, val):
        if not isinstance(val, self.type_):
            throw(ValueError, 'Value type for EnumConverter incorrect.')
        return val

    def sql2py(self, val):
        return int(val)

    @staticmethod
    def sql_type():
        return 'INTEGER'


class PGProvider(PGProvider_):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converter_classes.append((Enum, EnumConverter))
