from pony.orm import db_session, commit, select

from framework.models import db, Mod, User, Review


class DBHandler:
    def __init__(self, **kwargs):
        db.bind(provider='postgres', **kwargs)
        db.generate_mapping(create_tables=True)

    @property
    @db_session
    def mods(self):
        return list(Mod.select())

    @property
    @db_session
    def users(self):
        return list(User.select())

    @property
    @db_session
    def reviews(self):
        return list(Review.select())

    @db_session
    def new_mod(self, **kwargs):
        obj = Mod(**kwargs)

        commit()

        return obj

    @db_session
    def edit_mod(self, id_: str, **kwargs):
        mod = Mod[id_]
        mod.set(**kwargs)

    @db_session
    def new_user(self, **kwargs):
        obj = User(**kwargs)

        commit()

        return obj

    @db_session
    def edit_user(self, id_: str, **kwargs):
        user = User[id_]
        user.set(**kwargs)

    @db_session
    def new_review(self, **kwargs):
        obj = Review(**kwargs)

        commit()

        return obj
