# flake8: noqa: E128
"""
User reports

Revision ID: 0f0aacf8c646
Revises: 26b0c71d2c11
Create Date: 2019-06-08 13:27:55.721065+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as Enum


# revision identifiers, used by Alembic.
revision = '0f0aacf8c646'
down_revision = '26b0c71d2c11'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_report',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('content', sa.Unicode(length=1000), nullable=True),
        sa.Column('author_id', sa.Unicode(), nullable=True),
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('type', Enum('ipg_violation', 'conduct_violation', 'dmca', name='reporttype', create_type=False), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], name=op.f('fk_user_report_author_id_user'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_report_user_id_user'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_report'))
    )


def downgrade():
    op.drop_table('user_report')
