# flake8: noqa: E128
"""
Add ids to joining tables

Revision ID: 26b0c71d2c11
Revises: f3ceaef6a714
Create Date: 2019-05-10 09:34:03.509191+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '26b0c71d2c11'
down_revision = 'f3ceaef6a714'
branch_labels = None
depends_on = None


def upgrade():
    # Lambads to create new instances cause SA doesn't like reusing em :/
    id_ = lambda: sa.Column('id', sa.Unicode(), nullable=False)
    created_at = lambda: sa.Column('created_at', sa.DateTime(), nullable=True)

    op.add_column('mod_playtester', id_())
    op.add_column('mod_playtester', created_at())
    op.add_column('review_reaction', id_())
    op.add_column('review_reaction', created_at())
    op.add_column('user_favorite', id_())
    op.add_column('user_favorite', created_at())
    op.add_column('user_mod', id_())
    op.add_column('user_mod', created_at())


def downgrade():
    op.drop_column('user_mod', 'id')
    op.drop_column('user_mod', 'created_at')
    op.drop_column('user_favorite', 'id')
    op.drop_column('user_favorite', 'created_at')
    op.drop_column('review_reaction', 'id')
    op.drop_column('review_reaction', 'created_at')
    op.drop_column('mod_playtester', 'id')
    op.drop_column('mod_playtester', 'created_at')
