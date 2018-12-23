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

class Mod(db.Entity, Base):
    id = PrimaryKey(str)
    title = Required(str)
    icon = Optional(str, nullable=True)
    path = Required(str)
    media = Set(Media)
    tagline = Required(str)
    description = Required(str)
    website = Required(str)
    category = Required(int)
    released_at = Required(date)
    last_updated = Required(date)
    downloads = Required(int)
    authors = Set('User', reverse='mods')
    favorite_by = Set('User', reverse='favorites')
    reviews = Set('Review', reverse="mod")
    verified = Required(bool)
    status = Required(ModStatus)


class Connection(db.Entity, Base):
    name = Required(str)
    type = Required(ConnectionType)


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
