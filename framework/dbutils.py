# Stdlib
from enum import Enum

# External Libraries
from pony.orm.dbapiprovider import Converter
from pony.orm.dbproviders.postgres import PGProvider as PGProvider_
from pony.utils import throw


class EnumConverter(Converter):
    type_: type

    def init(self, kwargs):
        self.type_ = self.attr.py_type

    def validate(self, val, obj=None):
        if not isinstance(val, self.type_):
            throw(ValueError, 'Value type for EnumConverter incorrect.')
        return val

    def py2sql(self, val):
        return val.value

    def sql2py(self, val):
        return self.type_(int(val))

    @staticmethod
    def sql_type():
        return 'INTEGER'


class PGProvider(PGProvider_):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converter_classes.append((Enum, EnumConverter))
