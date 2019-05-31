# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ReportType


class UserReport(db.Model, Base):
    __tablename__ = "user_report"

    content = db.Column(db.Unicode(1000))
    author_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    user_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    type = db.Column(db.Enum(ReportType))
