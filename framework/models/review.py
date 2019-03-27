# Sayonika Internals
from framework.objects import db

from .base import Base


class Review(db.Model, Base):
    __tablename__ = "reviews"

    rating = db.Column(db.Numeric())
    content = db.Column(db.Unicode(2000))
    title = db.Column(db.Unicode(32))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
    author_id = db.Column(None, db.ForeignKey("users.id"))


class ReviewUpvoters(db.Model):
    __tablename__ = "review_upvoters"

    review_id = db.Column(None, db.ForeignKey("reviews.id"))
    user_id = db.Column(None, db.ForeignKey("users.id"))


class ReviewDownvoters(db.Model):
    __tablename__ = "review_downvoters"

    review_id = db.Column(None, db.ForeignKey("reviews.id"))
    user_id = db.Column(None, db.ForeignKey("users.id"))


class ReviewFunnys(db.Model):
    __tablename__ = "review_funnys"

    review_id = db.Column(None, db.ForeignKey("reviews.id"))
    user_id = db.Column(None, db.ForeignKey("users.id"))
