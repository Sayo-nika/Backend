# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ReportType


class Report(db.Model, Base):
    __tablename__ = "report"

    content = db.Column(db.Unicode(1000))
    author_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))
    type = db.Column(db.Enum(ReportType))
