# Stdlib
from enum import Enum

# External Libraries
from pony.orm import Set, Database, Optional, Required, PrimaryKey, db_session

db = Database()


class Base:
    @classmethod
    @db_session
    def exists(cls, id_: str):
        return cls.get(id=id_) is not None  # pylint: disable=no-member

    @classmethod
    @db_session
    def get_s(cls, arg):
        return cls.get(id=arg)  # pylint: disable=no-member

    @property
    @db_session
    def json(self):
        return self.__class__[self.id].to_dict(with_collections=True)  # pylint: disable=no-member


class ModStatus(Enum):
    Planning = 1
    InDevelop = 2
    PlayTesting = 3
    Released = 4
    Verified = 5


class Mod(db.Entity, Base):
    id = PrimaryKey(str)
    title = Required(str)
    icon = Optional(str, nullable=True)
    path = Required(str)
    # TODO: Media
    tagline = Required(str)
    description = Required(str)
    website = Required(str)
    # TODO: Category
    released_at = Required(int)
    last_updated = Required(int)
    downloads = Required(int)
    authors = Set('User', reverse='mods')
    favorite_by = Set('User', reverse='favorites')
    reviews = Set('Review', reverse="mod")
    verified = Required(bool)
    status = Required(ModStatus)


# Handles the Connection type
# Has two properties, and that's about it.
class Connection(db.Entity, Base):
    name = Required(str)
    #  Type will be having a range of what provider it is.
    #  Sadly, I didn't account for the int ranges per-provider
    #  so this will be defined impromptu.
    type = Required(int)


class User(db.Entity, Base):
    @property
    def json(self):
        return self.__class__[self.id].to_dict(with_collections=True, exclude=("password", "email"))

    id = PrimaryKey(str)
    email = Required(str)
    username = Required(str)
    avatar = Optional(str, nullable=True)
    donator = Required(bool)
    developer = Required(bool)
    moderator = Required(bool)
    bio = Optional(str, nullable=True)
    mods = Set(Mod)
    # FIXME: Set email_verfied by default to false!
    email_verified = Required(bool)
    editor = Required(bool)
    favorites = Set(Mod)
    connections = Set(Connection)
    reviews = Set('Review', reverse="author")
    upvoted = Set('Review', reverse='upvoters')
    downvoted = Set('Review', reverse='downvoters')
    helpful = Set('Review', reverse='helpfuls')
    password = Required(bytes)
    lastPassReset = Optional(int, nullable=True)

class Review(db.Entity, Base):
    id = PrimaryKey(str)
    rating = Required(str)
    mod = Required(Mod)
    content = Required(str)
    author = Required(User)
    upvoters = Set(User)
    downvoters = Set(User)
    helpfuls = Set(User)
