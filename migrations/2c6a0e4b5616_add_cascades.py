# flake8: noqa: E128
"""
Add cascades

Revision ID: 2c6a0e4b5616
Revises: 3007e0d40f26
Create Date: 2019-05-02 10:57:00.579594+00:00
"""
import re

# External Libraries
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c6a0e4b5616'
down_revision = '3007e0d40f26'
branch_labels = None
depends_on = None

constraint_re = re.compile(
    r"^fk_"  # Start tag
    r"(.*)_"  # Table
    r"((?:author|user|mod|review)(?:_id)?)_"  # Column
    r"(.*)$"  # Foreign table
)

constraints = [
    "fk_connection_user_user",
    "fk_editors_choice_author_id_user",
    "fk_editors_choice_mod_id_mod",
    "fk_media_mod_id_mod",
    "fk_mod_playtester_mod_id_mod",
    "fk_mod_playtester_user_id_user",
    "fk_report_author_id_user",
    "fk_report_mod_id_mod",
    "fk_review_author_id_user",
    "fk_review_mod_id_mod",
    "fk_review_reaction_review_id_review",
    "fk_review_reaction_user_id_user",
    "fk_user_favorite_user_id_user",
    "fk_user_favorite_mod_id_mod",
    "fk_user_mod_user_id_user",
    "fk_user_mod_mod_id_mod"
]


def upgrade():
    for constraint in constraints:
        # Get all parts of constraint (table[_table part 2]_column[_column part 2]_foreign_table)
        table, column, foreign = constraint_re.match(constraint).groups()

        op.drop_constraint(constraint, table, type_="foreignkey")
        op.create_foreign_key(op.f(constraint), table, foreign, [column], ['id'], ondelete='CASCADE')


def downgrade():
    for constraint in constraints:
        # Get all parts of constraint (table[_table part 2]_column[_column part 2]_foreign_table)
        table, column, foreign = constraint_re.match(constraint).groups()

        op.drop_constraint(op.f(constraint), table, type_="foreignkey")
        op.create_foreign_key(constraint, table, foreign, [column], ['id'])
