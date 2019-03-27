# flake8: noqa: E128
"""
Rename found helpful for reviews to found funny

Revision ID: f7b85c97502d
Revises: 593d015e8bff
Create Date: 2019-03-27 10:12:23.056588+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7b85c97502d'
down_revision = '593d015e8bff'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("review_helpfuls", "review_funnys")


def downgrade():
    op.rename_table("review_funnys", "review_helpfuls")
