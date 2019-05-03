# flake8: noqa: E128
"""
Generalized titles

Revision ID: f3ceaef6a714
Revises: 2c6a0e4b5616
Create Date: 2019-05-03 12:43:18.326629+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3ceaef6a714'
down_revision = '2c6a0e4b5616'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mod', sa.Column('generalized_title', sa.Unicode(), nullable=True))
    op.create_unique_constraint(op.f('uq_mod_generalized_title'), 'mod', ['generalized_title'])


def downgrade():
    op.drop_constraint(op.f('uq_mod_generalized_title'), 'mod', type_='unique')
    op.drop_column('mod', 'generalized_title')
