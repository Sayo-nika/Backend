# Stdlib
from datetime import datetime

# Sayonika Internals
from framework.objects import db
from .base import Base
from .enums import ModCategory, ModStatus


class Mod(db.Model, Base):
    __tablename__ = "mods"

    title = db.Column(db.Unicode(64), unique=True)
    icon = db.Column(db.Unicode(), nullable=True)
    tagline = db.Column(db.Unicode(100))
    description = db.Column(db.Unicode(10000))
    website = db.Column(db.Unicode())
    category = db.Column(db.Enum(ModCategory), default=Category.Unassigned)
    nsfw = db.Column(db.Boolean(), default=False)
    released_at = db.Column(db.Date(), nullable=True)
    last_updated = db.Column(db.DateTime(), default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.Enum(ModStatus))
    downloads = db.Column(db.BigInteger(), default=0)
    download_url = db.Column(db.Unicode(), nullable=True)
    verified = db.Column(db.Boolean(), default=False)

