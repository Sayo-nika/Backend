# Stdlib
from datetime import datetime

# External Libraries
from sqlalchemy.engine.default import DefaultExecutionContext

# Sayonika Internals
from framework.objects import db
from framework.utils import generalize_text

from .base import Base
from .enums import ModColor, ModStatus, AuthorRole, ModCategory


def create_generalized_title(context: DefaultExecutionContext) -> str:
    title = context.get_current_parameters()["title"]
    return generalize_text(title)


class Mod(db.Model, Base):
    __tablename__ = "mod"

    title = db.Column(db.Unicode(64), unique=True)
    generalized_title = db.Column(db.Unicode(), unique=True, default=create_generalized_title,
                                  onupdate=create_generalized_title)
    icon = db.Column(db.Unicode())
    banner = db.Column(db.Unicode())
    tagline = db.Column(db.Unicode(100))
    description = db.Column(db.Unicode(10000))
    website = db.Column(db.Unicode())
    is_private_beta = db.Column(db.Boolean(), default=False)
    category = db.Column(db.Enum(ModCategory), default=ModCategory.unassigned)
    nsfw = db.Column(db.Boolean(), default=False)
    theme_color = db.Column(db.Enum(ModColor))
    released_at = db.Column(db.Date(), nullable=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Enum(ModStatus))
    # TODO: probably turn this into a table and have better metrics for determining DLs
    downloads = db.Column(db.BigInteger(), default=0)
    download_url = db.Column(db.Unicode(), nullable=True)
    verified = db.Column(db.Boolean(), default=False)

    def to_dict(self):
        return {
            k: v for k, v in super().to_dict().items() if k not in ("generalized_title",)
        }


class ModAuthor(db.Model, Base):
    __tablename__ = "user_mod"

    role = db.Column(db.Enum(AuthorRole), default=AuthorRole.unassigned)
    user_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))


class ModPlaytester(db.Model, Base):
    __tablename__ = "mod_playtester"

    user_id = db.Column(None, db.ForeignKey("user.id", ondelete="CASCADE"))
    mod_id = db.Column(None, db.ForeignKey("mod.id", ondelete="CASCADE"))
