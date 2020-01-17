# flake8: noqa: E128
"""
IPFS migrate

Revision ID: c4ac52456d9c
Revises: 0f0aacf8c646
Create Date: 2020-01-17 12:18:02.022665+00:00
"""
# External Libraries
from alembic import op
import gino
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c4ac52456d9c"
down_revision = "0f0aacf8c646"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "userreport",
        sa.Column("id", sa.Unicode(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("content", sa.Unicode(length=1000), nullable=True),
        sa.Column("author_id", sa.Unicode(), nullable=True),
        sa.Column("user_id", sa.Unicode(), nullable=True),
        sa.Column(
            "type",
            postgresql.ENUM(
                "illegal_content",
                "harrasment",
                "spam",
                "tos_violation",
                name="userreporttype",
            ),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], name=op.f("fk_userreport_author_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_userreport_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_userreport")),
    )

    op.drop_table("user_report")
    op.add_column("media", sa.Column("hash", sa.Unicode(), nullable=True))
    op.drop_column("media", "url")


def downgrade():
    op.add_column(
        "media", sa.Column("url", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.drop_column("media", "hash")
    op.create_table(
        "user_report",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "content", sa.VARCHAR(length=1000), autoincrement=False, nullable=True
        ),
        sa.Column("author_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("user_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "type",
            postgresql.ENUM(
                "ipg_violation", "conduct_violation", "dmca", name="reporttype"
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["user.id"],
            name="fk_user_report_author_id_user",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_user_report_user_id_user",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_report"),
    )

    op.drop_table("userreport")
