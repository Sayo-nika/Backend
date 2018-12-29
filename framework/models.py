# Stdlib
from enum import Enum
from datetime import date

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

    @classmethod
    @db_session
    def get_any(cls, lower=False, **kwargs):
        def selector(item):
            if type(lower) is list:
                return any(True for k, v in kwargs if getattr(getattr(item, k),
                          'lower' if k in lower else '', lambda: k)() ==
                          getattr(v, 'lower' if k in lower else '', lambda: v)())
            elif lower is True:
                return any(True for k, v in kwargs if getattr(item, k).lower() == v.lower())
            else:
                return any(True for k, v in kwargs if getattr(item, k) == v)

        return cls.select(selector)

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


class ConnectionType(Enum):
    GitHub = 1
    GitLab = 2
    Discord = 3


class MediaType(Enum):
    Video = 1
    Image = 2


class Media(db.Entity, Base):
    type = Required(MediaType)
    url = Required(str)
    mod = Required(lambda: Mod)

class Mod(db.Entity, Base):
    id = PrimaryKey(str)
    title = Required(str, unique=True)
    icon = Optional(str, nullable=True)
    path = Required(str)
    media = Set(Media, reverse="mod")
    mod_content = Required(str)
    tagline = Required(str)
    description = Required(str)
    website = Required(str)
    category = Required(int)
    released_at = Required(date)
    last_updated = Required(date)
    downloads = Required(int)
    authors = Set(lambda: User, reverse='mods')
    favorited_by = Set(lambda: User, reverse='favorites')
    reviews = Set(lambda: Review, reverse="mod")
    repors = Set(lambda: Report, reverse="mod")
    verified = Required(bool)
    status = Required(ModStatus)


class Connection(db.Entity, Base):
    name = Required(str)
    type = Required(ConnectionType)
    user = Required(lambda: User)


class User(db.Entity, Base):
    @property
    def json(self):
        return self.__class__[self.id].to_dict(with_collections=True, exclude=("password", "email"))

    id = PrimaryKey(str)
    email = Required(str, unique=True)
    username = Required(str, unique=True)
    avatar = Optional(str, nullable=True)
    supporter = Required(bool)
    developer = Required(bool)
    moderator = Required(bool)
    editor = Required(bool)
    bio = Optional(str, nullable=True)
    mods = Set(Mod)
    email_verified = Required(bool, default=False)
    favorites = Set(Mod)
    reports = Set(lambda: Report, reverse="author")
    connections = Set(Connection, reverse="user")
    reviews = Set(lambda: Review, reverse="author")
    upvoted = Set(lambda: Review, reverse='upvoters')
    downvoted = Set(lambda: Review, reverse='downvoters')
    found_helpful = Set(lambda: Review, reverse='helpfuls')
    password = Required(bytes)
    last_pass_reset = Optional(int, nullable=True)

class Review(db.Entity, Base):
    id = PrimaryKey(str)
    rating = Required(int)
    mod = Required(Mod)
    content = Required(str)
    author = Required(User)
    upvoters = Set(User)
    downvoters = Set(User)
    helpfuls = Set(User)

class Report(db.Entity, Base):
    id = PrimaryKey(str)
    conntent = Required(str)
    author = Required(User)
    mod = Required(Mod)