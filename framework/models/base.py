# Stdlib
from datetime import datetime
from typing import List, Union

# External Libraries
from gino import Gino
from simpleflake import simpleflake
from sqlalchemy import or_, func

# Sayonika Internals
from framework.objects import db


class Base:
    """Base utility class for models to inherit from."""
    id = db.Column(db.Unicode(), primary_key=True, default=lambda: str(simpleflake()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    async def exists(cls: db.Model, id_: str) -> bool:
        """Check if a model exists with the given id."""
        return bool(await cls.select("id").where(cls.id == id_).gino.scalar())

    @classmethod
    def get_any(cls: db.Model, insensitive: Union[bool, List[str]] = False, **kwargs) -> Gino:
        """Get models that match any of the given kwargs, with them optionally being case insensitive."""
        if not kwargs:
            raise ValueError("No kwargs provided")

        queries = []

        if isinstance(insensitive, list):
            for k, v in kwargs:
                if k in insensitive:
                    queries.push(func.lower(getattr(cls, k)) == func.lower(v))
                else:
                    queries.push(getattr(cls, k) == v)
        elif insensitive is True:
            queries = [func.lower(getattr(cls, k)) == func.lower(v) for k, v in kwargs.items()]
        else:
            queries = [getattr(cls, k) == v for k, v in kwargs.items()]

        return cls.query.where(or_(*queries)).gino
