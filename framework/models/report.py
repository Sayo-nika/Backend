# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ReportType


class Report(db.Model, Base):
    __tablename__ = "reports"

    content = db.Column(db.Unicode(1000))
    author_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
    type = db.Column(db.Enum(ReportType))
