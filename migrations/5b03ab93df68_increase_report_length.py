# flake8: noqa: E128
"""
increase report length

Revision ID: 5b03ab93df68
Revises: cb6ace8c7786
Create Date: 2019-04-09 04:10:51.136691+00:00
"""
# External Libraries
from alembic import op
import gino
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b03ab93df68'
down_revision = 'cb6ace8c7786'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('reports', 'content',
               existing_type=sa.Unicode(200),
               type_=sa.Unicode(1000),
               existing_nullable=False)


def downgrade():
    op.alter_column('reports', 'content',
               existing_type=sa.Unicode(1000),
               type_=sa.Unicode(200),
               existing_nullable=False)
