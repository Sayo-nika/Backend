# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ConnectionType


class Connection(db.Model, Base):
    __tablename__ = "connection"

    name = db.Column(db.Unicode())
    type = db.Column(db.Enum(ConnectionType))
    user = db.Column(None, db.ForeignKey("user.id"))
