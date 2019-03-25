# Sayonika Internals
from framework.objects import db

from .base import Base

COMMON_FILTERED = ("password", "last_pass_reset", "email_verified")
DEFAULT_FILTERED = (*COMMON_FILTERED, "email")


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

    def to_dict(self):
        return {
            k: v for k, v in super().to_dict().items() if k not in DEFAULT_FILTERED
        }

    def to_self_dict(self):
        """
        Converts the model to a dict, but keeps `email` in.
        Used for the `/users/@me` endpoint in particular.
        """
        return {
            k: v for k, v in super().to_dict().items() if k not in COMMON_FILTERED
        }


class UserFavorites(db.Model):
    __tablename__ = "user_favourites"

    user_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
