# flake8: noqa: E128
"""
Initial migration

Revision ID: a7e5616b80f8
Revises:
Create Date: 2019-03-12 09:46:37.398599+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa

# Sayonika Internals
from framework.models import MediaType, ModStatus, AuthorRole, ModCategory, ConnectionType

# revision identifiers, used by Alembic.
revision = "a7e5616b80f8"
down_revision = None
branch_labels = None
depends_on = None

# Create SQLAlchemy enum types here to prevent duplication later on. Needed since Alembic doesn't auto-drop enums
# and often doesn't auto-create them, so we gotta do that manually.
enums = {
    "media_type": sa.Enum(MediaType),
    "mod_status": sa.Enum(ModStatus),
    "author_role": sa.Enum(AuthorRole),
    "mod_category": sa.Enum(ModCategory),
    "connection_type": sa.Enum(ConnectionType)
}


def upgrade():
    op_bind = op.get_bind()

    for enum in enums.values():
        enum.create(op_bind, checkfirst=False)

    op.create_table("mods",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("title", sa.Unicode(length=64), nullable=True),
        sa.Column("icon", sa.Unicode(), nullable=True),
        sa.Column("banner", sa.Unicode(), nullable=True),
        sa.Column("tagline", sa.Unicode(length=100), nullable=True),
        sa.Column("description", sa.Unicode(length=10000), nullable=True),
        sa.Column("website", sa.Unicode(), nullable=True),
        sa.Column("is_private_beta", sa.Boolean(), nullable=True),
        sa.Column("category", enums["mod_category"], nullable=True),
        sa.Column("nsfw", sa.Boolean(), nullable=True),
        sa.Column("released_at", sa.Date(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.Column("status", enums["mod_status"], nullable=True),
        sa.Column("downloads", sa.BigInteger(), nullable=True),
        sa.Column("download_url", sa.Unicode(), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title")
    )
    op.create_table("users",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("email", sa.Unicode(), nullable=True),
        sa.Column("username", sa.Unicode(length=25), nullable=True),
        sa.Column("avatar", sa.Unicode(), nullable=True),
        sa.Column("bio", sa.Unicode(length=100), nullable=True),
        sa.Column("supporter", sa.Boolean(), nullable=True),
        sa.Column("developer", sa.Boolean(), nullable=True),
        sa.Column("moderator", sa.Boolean(), nullable=True),
        sa.Column("editor", sa.Boolean(), nullable=True),
        sa.Column("joined_at", sa.DateTime(), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=True),
        sa.Column("password", sa.Binary(), nullable=True),
        sa.Column("last_pass_reset", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username")
    )
    op.create_table("connections",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("name", sa.Unicode(), nullable=True),
        sa.Column("type", enums["connection_type"], nullable=True),
        sa.Column("user", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["user"], ["users.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table("editors_choice",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.Column("featured", sa.Boolean(), nullable=True),
        sa.Column("editors_notes", sa.Unicode(length=500), nullable=True),
        sa.Column("author_id", sa.Unicode(), nullable=True),
        sa.Column("article_url", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table("media",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("type", enums["media_type"], nullable=True),
        sa.Column("url", sa.Unicode(), nullable=True),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table("mod_playtesters",
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"])
    )
    op.create_table("reports",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("content", sa.Unicode(length=200), nullable=True),
        sa.Column("author_id", sa.Unicode(), nullable=True),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table("reviews",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("rating", sa.Numeric(), nullable=True),
        sa.Column("content", sa.Unicode(length=2000), nullable=True),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.Column("author_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table("user_favourites",
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"])
    )
    op.create_table("user_mods",
        sa.Column("role", enums["author_role"], nullable=True),
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.Column("mod_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["mod_id"], ["mods.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"])
    )
    op.create_table("review_downvoters",
        sa.Column("review_id", sa.Unicode(), nullable=True),
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"])
    )
    op.create_table("review_helpfuls",
        sa.Column("review_id", sa.Unicode(), nullable=True),
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"])
    )
    op.create_table("review_upvoters",
        sa.Column("review_id", sa.Unicode(), nullable=True),
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"])
    )


def downgrade():
    op.drop_table("review_upvoters")
    op.drop_table("review_helpfuls")
    op.drop_table("review_downvoters")
    op.drop_table("user_mods")
    op.drop_table("user_favourites")
    op.drop_table("reviews")
    op.drop_table("reports")
    op.drop_table("mod_playtesters")
    op.drop_table("media")
    op.drop_table("editors_choice")
    op.drop_table("connections")
    op.drop_table("users")
    op.drop_table("mods")

    op_bind = op.get_bind()

    for enum in enums.values():
        enum.drop(op_bind, checkfirst=False)
