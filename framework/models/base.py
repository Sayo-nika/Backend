# Sayonika Internals
from framework.objects import db


class Base:
    id = db.Column(db.Unicode(), primary_key=True)

    # @classmethod
    # def exists(cls, id_: str):
    #     return cls.get(id=id_) is not None  # pylint: disable=no-member

    # @classmethod
    # def get_s(cls, arg):
    #     return cls.get(id=arg)  # pylint: disable=no-member

    # @classmethod
    # def get_any(cls, lower=False, **kwargs):
    #     def selector(item):
    #         if type(lower) is list:
    #             return any(True for k, v in kwargs if getattr(getattr(item, k),
    #                       'lower' if k in lower else '', lambda: k)() ==
    #                       getattr(v, 'lower' if k in lower else '', lambda: v)())
    #         elif lower is True:
    #             return any(True for k, v in kwargs if getattr(item, k).lower() == v.lower())
    #         else:
    #             return any(True for k, v in kwargs if getattr(item, k) == v)

    #     return cls.select(selector)

    # @property
    # def json(self):
    #     return self.__class__[self.id].to_dict(with_collections=True)  # pylint: disable=no-member
