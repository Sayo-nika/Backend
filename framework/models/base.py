# Stdlib
from typing import List, Union

# External Libraries
from sqlalchemy import or_, func

# Sayonika Internals
from framework.objects import db


class Base:
    id = db.Column(db.Unicode(), primary_key=True)

    @classmethod
    def get_any(cls: db.Model, insensitive: Union[bool, List[str]]=False, **kwargs):
        if not len(kwargs):
            raise ValueError('No kwargs provided')

        queries = []

        if type(insensitive) is list:
            for k, v in kwargs:
                if k in insensitive:
                    queries.push(func.lower(getattr(cls, k)) == func.lower(v))
                else:
                    queries.push(getattr(cls, k) == v)
        elif insensitive is True:
            queries = [func.lower(getattr(cls, k)) == func.lower(v) for k, v in kwargs]
        else:
            queries = [getattr(cls, k) == v for k, v in kwargs]

        return cls.query.where(or_(*queries)).gino
