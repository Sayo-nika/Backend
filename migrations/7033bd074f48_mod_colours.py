# flake8: noqa: E128
"""
Mod colours

Revision ID: 7033bd074f48
Revises: a7e5616b80f8
Create Date: 2019-03-19 09:38:47.848920+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa

# Sayonika Internals
from framework.models import ModColor

# revision identifiers, used by Alembic.
revision = '7033bd074f48'
down_revision = 'a7e5616b80f8'
branch_labels = None
depends_on = None

mod_color = sa.Enum(ModColor)


def upgrade():
    mod_color.create(op.get_bind(), checkfirst=False)

    op.add_column('mods',
        sa.Column('theme_color', mod_color, nullable=True)
    )


def downgrade():
    op.drop_column('mods', 'theme_color')
    mod_color.drop(op.get_bind(), checkfirst=False)
