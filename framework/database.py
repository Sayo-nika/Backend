# External Libraries
from pony.orm import commit, db_session

# Sayonika Internals
from framework.dbutils import PGProvider
from framework.models import Mod, User, Review, db


class DBHandler:
    def __init__(self, **kwargs):
        db.bind(provider=PGProvider, **kwargs)
        db.generate_mapping(create_tables=True)

    @property
    @db_session
    def mods(self) -> list:
        return list(Mod.select())

    @property
    @db_session
    def users(self) -> list:
        return list(User.select())

    @property
    @db_session
    def reviews(self) -> list:
        return list(Review.select())

    @staticmethod
    @db_session
    def new_mod(**kwargs):
        obj = Mod(**kwargs)

        commit()

        return obj

    @staticmethod
    @db_session
    def edit_mod(id_: str, **kwargs):
        mod = Mod[id_]
        mod.set(**kwargs)

    @staticmethod
    @db_session
    def new_user(**kwargs):
        obj = User(**kwargs)

        commit()

        return obj

    @staticmethod
    @db_session
    def edit_user(id_: str, **kwargs):
        user = User[id_]
        user.set(**kwargs)

    @staticmethod
    @db_session
    def new_review(**kwargs):
        obj = Review(**kwargs)

        commit()

        return obj
