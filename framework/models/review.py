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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._upvotes = []
        self._downvotes = []
        self._funnys = []

    @property
    def upvotes(self):
        return self._upvotes

    @property
    def downvotes(self):
        return self._downvotes

    @property
    def funnys(self):
        return self._funnys

    @upvotes.setter
    def upvotes(self, value: "ReviewReaction"):
        self._upvotes.append(value)

    @downvotes.setter
    def downvotes(self, value: "ReviewReaction"):
        self._downvotes.append(value)

    @funnys.setter
    def funnys(self, value: "ReviewReaction"):
        self._funnys.append(value)

    def to_dict(self):
        return {
            **{k: v for k, v in super().to_dict},
            "upvotes": self._upvotes,
            "downvotes": self._downvotes,
            "funnys": self._funnys,
        }

class ReviewReaction(db.Model, Base):
    __tablename__ = "review_reaction"

    review_id = db.Column(None, db.ForeignKey("review.id", ondelete="CASCADE"))
    user_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    reaction = db.Column(db.Enum(ReactionType), nullable=False)
