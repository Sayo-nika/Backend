# Stdlib
from typing import List, Union

# External Libraries
from simpleflake import simpleflake
from sqlalchemy import or_, func, exists

# Sayonika Internals
from framework.objects import db


class Base:
    id = db.Column(db.Unicode(), primary_key=True, default=lambda: str(simpleflake()))

    @classmethod
    async def exists(cls: db.Model, id: str):
        return await cls.query(exists().where(cls.id == id)).gino.scalar()

    @classmethod
    def get_any(cls: db.Model, insensitive: Union[bool, List[str]] = False, **kwargs):
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

    @classmethod
    def paginate(cls: db.Model, page: int, limit: int = 50):
        page = page - 1 if page > 0 else 0

        return cls.query.limit(limit).offset(page * limit)
