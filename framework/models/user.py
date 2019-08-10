# External Libraries
from sqlalchemy.engine.default import DefaultExecutionContext

# Sayonika Internals
from framework.objects import db
from framework.utils import generate_gravatar

from .base import Base
from .mod import ModAuthor

COMMON_FILTERED = ("password", "last_pass_reset", "email_verified")
DEFAULT_FILTERED = (*COMMON_FILTERED, "email")


def create_default_avatar(context: DefaultExecutionContext) -> str:
    params = context.get_current_parameters()
    return generate_gravatar(params["email"])


class User(db.Model, Base):
    __tablename__ = "user"

    email = db.Column(db.Unicode(), unique=True)
    username = db.Column(db.Unicode(25), unique=True)
    avatar = db.Column(db.Unicode(), nullable=True, default=create_default_avatar)
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

        self._role = None
        self._role_name = None

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value: ModAuthor):
        self._role = value
        self._role_name = value.role.name

    def to_dict(self):
        return {
            **{k: v for k, v in super().to_dict().items() if k not in DEFAULT_FILTERED},
            "role": self._role_name,
            # "__": self._role.to_dict()
        }

    def to_self_dict(self):
        """
        Converts the model to a dict, but keeps `email` in.
        Used for the `/users/@me` endpoint in particular.
        """
        return {
            k: v for k, v in super().to_dict().items() if k not in COMMON_FILTERED
        }


class UserFavorite(db.Model, Base):
    __tablename__ = "user_favorite"

    user_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))
