# Sayonika Internals
from framework.objects import db

from .base import Base
from .enums import ReactionType


class Review(db.Model, Base):
    __tablename__ = "review"

    rating = db.Column(db.Numeric())
    content = db.Column(db.Unicode(2000))
    title = db.Column(db.Unicode(32))
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))
    author_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))


class ReviewReaction(db.Model):
    __tablename__ = "review_reaction"

    review_id = db.Column(None, db.ForeignKey("review.id", ondelete="CASCADE"))
    user_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    reaction = db.Column(db.Enum(ReactionType), nullable=False)
