# flake8: noqa: E128
"""
created_at

Revision ID: 593d015e8bff
Revises: 7033bd074f48
Create Date: 2019-03-25 07:50:00.097127+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "593d015e8bff"
down_revision = "7033bd074f48"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("connections", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("editors_choice", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("media", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("mods", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("reports", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("reviews", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.alter_column("users", "joined_at", new_column_name="created_at")


def downgrade():
    op.alter_column("users", "created_at", new_column_name="joined_at")
    op.drop_column("reviews", "created_at")
    op.drop_column("reports", "created_at")
    op.drop_column("mods", "created_at")
    op.drop_column("media", "created_at")
    op.drop_column("editors_choice", "created_at")
    op.drop_column("connections", "created_at")
