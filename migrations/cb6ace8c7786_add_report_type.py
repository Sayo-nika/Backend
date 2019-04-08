# flake8: noqa: E128
"""
add report type

Revision ID: cb6ace8c7786
Revises: a65877d5faaf
Create Date: 2019-04-08 12:45:32.656960+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa

# Sayonika Internals
from framework.models import ReportType

# revision identifiers, used by Alembic.
revision = 'cb6ace8c7786'
down_revision = 'a65877d5faaf'
branch_labels = None
depends_on = None

report_type = sa.Enum(ReportType)


def upgrade():
    report_type.create(op.get_bind(), checkfirst=False)

    op.add_column("reports",
        sa.Column("type", report_type, nullable=False)
    )


def downgrade():
    op.drop_column("reports", "type")
    report_type.drop(op.get_bind(), checkfirst=False)
