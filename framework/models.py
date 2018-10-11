from pony.orm import Required, Set, Database, PrimaryKey, db_session

db = Database()


class Base:
    @classmethod
    @db_session
    def exists(cls, id_: str):
        return cls.get(id=id_) is not None

    @classmethod
    @db_session
    def get_s(cls, arg):
        return cls.get(id=arg)

    @property
    def json(self):
        return self.to_json()


class Mod(db.Entity, Base):
    id = PrimaryKey(str)
    title = Required(str)
    path = Required(str)
    released_at = Required(int)
    last_updated = Required(int)
    downloads = Required(int)
    authors = Set('User', reverse='mods')
    favourite_by = Set('User', reverse='favorites')
    verified = Required(bool)


class User(db.Entity, Base):
    id = PrimaryKey(str)
    name = Required(str)
    bio = Required(str)
    mods = Set(Mod, reverse="authors")
    favorites = Set(Mod, reverse="favourite_by")


class Review(db.Entity, Base):
    id = PrimaryKey(str)
    mod = Required(str)
    message = Required(str)
    author = Required(str)
