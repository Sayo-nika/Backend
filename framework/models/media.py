# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import MediaType


class Media(db.Model, Base):
    __tablename__ = "media"

    type = db.Column(db.Enum(MediaType))
    url = db.Column(db.Unicode())
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))
