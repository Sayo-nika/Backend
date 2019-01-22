# Sayonika Internals
from framework.objects import db
from .base import Base


class User(db.Model, Base):
    __tablename__ = "users"

    email = db.Column(db.Unicode(), unique=True)
    username = db.Column(db.Unicode(25), unique=True)
    avatar = db.Column(db.Unicode(), nullable=True)
    bio = db.Column(db.Unicode(100), nullable=True)
    supporter = db.Column(db.Boolean(), default=False)
    developer = db.Column(db.Boolean(), default=False)
    moderator = db.Column(db.Boolean(), default=False)
    editor = db.Column(db.Boolean(), default=False)
    email_verified = db.Column(db.Boolean(), default=False)
    password = db.Column(db.Binary())
    last_pass_reset = db.Column(db.DateTime())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._mods = set()
        self._favorites = set()

    def to_dict(self):
        return {k: v for k, v in super().to_dict().items() if k not in ['password', 'email', 'last_pass_reset',
                'email_verified']}

    @property
    def mods(self):
        return self._mods

    @property
    def favourites(self):
        return self._favorites

    # reports = Set(lambda: Report, reverse="author")
    # connections = Set(Connection, reverse="user")
    # reviews = Set(lambda: Review, reverse="author")


class UserMods(db.Model):
    __tablename__ = "user_mods"

    user_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))


class UserFavorites(db.Model):
    __tablename__ = "user_favourites"

    user_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
