# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ReportType, UserReportType


class Report(db.Model, Base):
    __tablename__ = "report"

    content = db.Column(db.Unicode(1000))
    author_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))
    type = db.Column(db.Enum(ReportType))


class UserReport(db.Model, Base):
    __tablename__ = "userreport"  # No underscore, as its not a many-many relationship.

    content = db.Column(db.Unicode(1000))
    author_id = db.Column(None, db.ForeignKey("user.id"))
    user_id = db.Column(None, db.ForeignKey("user.id"))
    type = db.Column(db.Enum(UserReportType))
