# flake8: noqa: E128
"""
Add cascades

Revision ID: 2c6a0e4b5616
Revises: 3007e0d40f26
Create Date: 2019-05-02 10:57:00.579594+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c6a0e4b5616'
down_revision = '3007e0d40f26'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('fk_connection_user_user', 'connection', type_='foreignkey')
    op.create_foreign_key(op.f('fk_connection_user_user'), 'connection', 'user', ['user'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_editors_choice_author_id_user', 'editors_choice', type_='foreignkey')
    op.drop_constraint('fk_editors_choice_mod_id_mod', 'editors_choice', type_='foreignkey')
    op.create_foreign_key(op.f('fk_editors_choice_mod_id_mod'), 'editors_choice', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_editors_choice_author_id_user'), 'editors_choice', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_media_mod_id_mod', 'media', type_='foreignkey')
    op.create_foreign_key(op.f('fk_media_mod_id_mod'), 'media', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_mod_playtester_mod_id_mod', 'mod_playtester', type_='foreignkey')
    op.drop_constraint('fk_mod_playtester_user_id_user', 'mod_playtester', type_='foreignkey')
    op.create_foreign_key(op.f('fk_mod_playtester_mod_id_mod'), 'mod_playtester', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_mod_playtester_user_id_user'), 'mod_playtester', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_report_author_id_user', 'report', type_='foreignkey')
    op.drop_constraint('fk_report_mod_id_mod', 'report', type_='foreignkey')
    op.create_foreign_key(op.f('fk_report_mod_id_mod'), 'report', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_report_author_id_user'), 'report', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_review_author_id_user', 'review', type_='foreignkey')
    op.drop_constraint('fk_review_mod_id_mod', 'review', type_='foreignkey')
    op.create_foreign_key(op.f('fk_review_mod_id_mod'), 'review', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_review_author_id_user'), 'review', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_review_reaction_review_id_review', 'review_reaction', type_='foreignkey')
    op.drop_constraint('fk_review_reaction_user_id_user', 'review_reaction', type_='foreignkey')
    op.create_foreign_key(op.f('fk_review_reaction_review_id_review'), 'review_reaction', 'review', ['review_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_review_reaction_user_id_user'), 'review_reaction', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_user_favorite_user_id_user', 'user_favorite', type_='foreignkey')
    op.drop_constraint('fk_user_favorite_mod_id_mod', 'user_favorite', type_='foreignkey')
    op.create_foreign_key(op.f('fk_user_favorite_user_id_user'), 'user_favorite', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_user_favorite_mod_id_mod'), 'user_favorite', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_user_mod_user_id_user', 'user_mod', type_='foreignkey')
    op.drop_constraint('fk_user_mod_mod_id_mod', 'user_mod', type_='foreignkey')
    op.create_foreign_key(op.f('fk_user_mod_user_id_user'), 'user_mod', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_user_mod_mod_id_mod'), 'user_mod', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint(op.f('fk_user_mod_mod_id_mod'), 'user_mod', type_='foreignkey')
    op.drop_constraint(op.f('fk_user_mod_user_id_user'), 'user_mod', type_='foreignkey')
    op.create_foreign_key('fk_user_mod_mod_id_mod', 'user_mod', 'mod', ['mod_id'], ['id'])
    op.create_foreign_key('fk_user_mod_user_id_user', 'user_mod', 'user', ['user_id'], ['id'])
    op.drop_constraint(op.f('fk_user_favorite_mod_id_mod'), 'user_favorite', type_='foreignkey')
    op.drop_constraint(op.f('fk_user_favorite_user_id_user'), 'user_favorite', type_='foreignkey')
    op.create_foreign_key('fk_user_favorite_mod_id_mod', 'user_favorite', 'mod', ['mod_id'], ['id'])
    op.create_foreign_key('fk_user_favorite_user_id_user', 'user_favorite', 'user', ['user_id'], ['id'])
    op.drop_constraint(op.f('fk_review_reaction_user_id_user'), 'review_reaction', type_='foreignkey')
    op.drop_constraint(op.f('fk_review_reaction_review_id_review'), 'review_reaction', type_='foreignkey')
    op.create_foreign_key('fk_review_reaction_user_id_user', 'review_reaction', 'user', ['user_id'], ['id'])
    op.create_foreign_key('fk_review_reaction_review_id_review', 'review_reaction', 'review', ['review_id'], ['id'])
    op.drop_constraint(op.f('fk_review_author_id_user'), 'review', type_='foreignkey')
    op.drop_constraint(op.f('fk_review_mod_id_mod'), 'review', type_='foreignkey')
    op.create_foreign_key('fk_review_mod_id_mod', 'review', 'mod', ['mod_id'], ['id'])
    op.create_foreign_key('fk_review_author_id_user', 'review', 'user', ['author_id'], ['id'])
    op.drop_constraint(op.f('fk_report_author_id_user'), 'report', type_='foreignkey')
    op.drop_constraint(op.f('fk_report_mod_id_mod'), 'report', type_='foreignkey')
    op.create_foreign_key('fk_report_mod_id_mod', 'report', 'mod', ['mod_id'], ['id'])
    op.create_foreign_key('fk_report_author_id_user', 'report', 'user', ['author_id'], ['id'])
    op.drop_constraint(op.f('fk_mod_playtester_user_id_user'), 'mod_playtester', type_='foreignkey')
    op.drop_constraint(op.f('fk_mod_playtester_mod_id_mod'), 'mod_playtester', type_='foreignkey')
    op.create_foreign_key('fk_mod_playtester_user_id_user', 'mod_playtester', 'user', ['user_id'], ['id'])
    op.create_foreign_key('fk_mod_playtester_mod_id_mod', 'mod_playtester', 'mod', ['mod_id'], ['id'])
    op.drop_constraint(op.f('fk_media_mod_id_mod'), 'media', type_='foreignkey')
    op.create_foreign_key('fk_media_mod_id_mod', 'media', 'mod', ['mod_id'], ['id'])
    op.drop_constraint(op.f('fk_editors_choice_author_id_user'), 'editors_choice', type_='foreignkey')
    op.drop_constraint(op.f('fk_editors_choice_mod_id_mod'), 'editors_choice', type_='foreignkey')
    op.create_foreign_key('fk_editors_choice_mod_id_mod', 'editors_choice', 'mod', ['mod_id'], ['id'])
    op.create_foreign_key('fk_editors_choice_author_id_user', 'editors_choice', 'user', ['author_id'], ['id'])
    op.drop_constraint(op.f('fk_connection_user_user'), 'connection', type_='foreignkey')
    op.create_foreign_key('fk_connection_user_user', 'connection', 'user', ['user'], ['id'])
