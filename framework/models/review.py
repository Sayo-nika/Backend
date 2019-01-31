# Sayonika Internals
from framework.objects import db
from .base import Base


class Review(db.Model, Base):
    __tablename__ = "reviews"

    rating = db.Column(db.Numeric())
    content = db.Column(db.Unicode(2000))
    mod_id = db.Column(None, db.ForeignKey("mods.id"))
    author_id = db.Column(None, db.ForeignKey("users.id"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._upvoters = set()
        self._downvoters = set()
        self._helpfuls = set()

    @property
    def upvoters(self):
        return self._upvoters

    @property
    def downvoters(self):
        return self._downvoters

    @property
    def helpfuls(self):
        return self._helpfuls


class ReviewUpvoters(db.Model):
    __tablename__ = "review_upvoters"

    review_id = db.Column(None, db.ForeignKey("reviews.id"))
    user_id = db.Column(None, db.ForeignKey("users.id"))


class ReviewDownvoters(db.Model):
    __tablename__ = "review_downvoters"

    review_id = db.Column(None, db.ForeignKey("reviews.id"))
    user_id = db.Column(None, db.ForeignKey("users.id"))


class ReviewHelpfuls(db.Model):
    __tablename__ = "review_helpfuls"

    review_id = db.Column(None, db.ForeignKey("reviews.id"))
    user_id = db.Column(None, db.ForeignKey("users.id"))
