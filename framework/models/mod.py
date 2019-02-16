# Stdlib
from datetime import datetime

# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ModStatus, AuthorRole, ModCategory


class Mod(db.Model, Base):
    __tablename__ = "mods"

    title = db.Column(db.Unicode(64), unique=True)
    icon = db.Column(db.Unicode(), nullable=True)
    tagline = db.Column(db.Unicode(100))
    description = db.Column(db.Unicode(10000))
    website = db.Column(db.Unicode())
    is_private_beta = db.Column(db.Boolean(), default=False)
    category = db.Column(db.Enum(ModCategory), default=ModCategory.Unassigned)
    nsfw = db.Column(db.Boolean(), default=False)
    released_at = db.Column(db.Date(), nullable=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Enum(ModStatus))
    downloads = db.Column(db.BigInteger(), default=0)
    download_url = db.Column(db.Unicode(), nullable=True)
    verified = db.Column(db.Boolean(), default=False)


class ModAuthors(db.Model):
    __tablename__ = "user_mods"

    role = db.Column(db.Enum(AuthorRole), default=AuthorRole.Unassigned)
    user_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))

class Playtesters(db.Model):
    __tablename__ = "mod_playtesters"

    user_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
