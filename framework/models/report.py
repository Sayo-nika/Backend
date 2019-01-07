# Sayonika Internals
from framework.objects import db
from base import Base


class Report(db.Model, Base):
    __tablename__ = "reports"

    content = db.Column(db.Unicode(200))
    author_id = db.Column(None, db.ForeignKey("users.id"))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
