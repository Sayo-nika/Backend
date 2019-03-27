# flake8: noqa: E128
"""
Review titles

Revision ID: a65877d5faaf
Revises: f7b85c97502d
Create Date: 2019-03-27 11:03:06.972514+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a65877d5faaf'
down_revision = 'f7b85c97502d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reviews', sa.Column('title', sa.Unicode(length=32), nullable=True))


def downgrade():
    op.drop_column('reviews', 'title')
