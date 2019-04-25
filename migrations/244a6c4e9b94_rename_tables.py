# flake8: noqa: E128
"""
rename tables

Revision ID: 244a6c4e9b94
Revises: 5b03ab93df68
Create Date: 2019-04-24 14:41:29.150763+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '244a6c4e9b94'
down_revision = '5b03ab93df68'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('mod',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.Unicode(length=64), nullable=True),
        sa.Column('icon', sa.Unicode(), nullable=True),
        sa.Column('banner', sa.Unicode(), nullable=True),
        sa.Column('tagline', sa.Unicode(length=100), nullable=True),
        sa.Column('description', sa.Unicode(length=10000), nullable=True),
        sa.Column('website', sa.Unicode(), nullable=True),
        sa.Column('is_private_beta', sa.Boolean(), nullable=True),
        sa.Column('category', sa.Enum('unassigned', 'tools', 'comedy', 'tragic_comedy', 'drama', 'rom_com', 'romance', 'horror', 'mystery', 'satire', 'thriller', 'sci_fi', name='modcategory'), nullable=True),
        sa.Column('nsfw', sa.Boolean(), nullable=True),
        sa.Column('theme_color', sa.Enum('default', 'red', 'pink', 'purple', 'deep_purple', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange', 'deep_orange', name='modcolor'), nullable=True),
        sa.Column('released_at', sa.Date(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('archived', 'planning', 'in_development', 'playtesting', 'released', name='modstatus'), nullable=True),
        sa.Column('downloads', sa.BigInteger(), nullable=True),
        sa.Column('download_url', sa.Unicode(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_mod')),
        sa.UniqueConstraint('title', name=op.f('uq_mod_title'))
    )
    op.create_table('user',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('email', sa.Unicode(), nullable=True),
        sa.Column('username', sa.Unicode(length=25), nullable=True),
        sa.Column('avatar', sa.Unicode(), nullable=True),
        sa.Column('bio', sa.Unicode(length=100), nullable=True),
        sa.Column('supporter', sa.Boolean(), nullable=True),
        sa.Column('developer', sa.Boolean(), nullable=True),
        sa.Column('moderator', sa.Boolean(), nullable=True),
        sa.Column('editor', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('password', sa.Binary(), nullable=True),
        sa.Column('last_pass_reset', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('email', name=op.f('uq_user_email')),
        sa.UniqueConstraint('username', name=op.f('uq_user_username'))
    )
    op.create_table('connection',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.Unicode(), nullable=True),
        sa.Column('type', sa.Enum('github', 'gitlab', 'discord', name='connectiontype'), nullable=True),
        sa.Column('user', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['user'], ['user.id'], name=op.f('fk_connection_user_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_connection'))
    )
    op.create_table('mod_playtester',
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_mod_playtester_mod_id_mod')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_mod_playtester_user_id_user'))
    )
    op.create_table('report',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('content', sa.Unicode(length=1000), nullable=True),
        sa.Column('author_id', sa.Unicode(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.Column('type', sa.Enum('ipg_violation', 'conduct_violation', 'dmca', name='reporttype'), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], name=op.f('fk_report_author_id_user')),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_report_mod_id_mod')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_report'))
    )
    op.create_table('review',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Numeric(), nullable=True),
        sa.Column('content', sa.Unicode(length=2000), nullable=True),
        sa.Column('title', sa.Unicode(length=32), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.Column('author_id', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], name=op.f('fk_review_author_id_user')),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_review_mod_id_mod')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_review'))
    )
    op.create_table('user_favorite',
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_user_favorite_mod_id_mod')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_favorite_user_id_user'))
    )
    op.create_table('user_mod',
        sa.Column('role', sa.Enum('unassigned', 'owner', 'co_owner', 'programmer', 'artist', 'writer', 'musician', 'public_relations', name='authorrole'), nullable=True),
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_user_mod_mod_id_mod')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_mod_user_id_user'))
    )
    op.create_table('review_reaction',
        sa.Column('review_id', sa.Unicode(), nullable=True),
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('reaction', sa.Enum('upvote', 'downvote', 'funny', name='reactiontype'), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['review.id'], name=op.f('fk_review_reaction_review_id_review')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_review_reaction_user_id_user'))
    )

    op.drop_table('user_mods')
    op.drop_table('review_funnys')
    op.drop_table('mod_playtesters')
    op.drop_table('user_favourites')
    op.drop_table('review_downvoters')
    op.drop_table('users')
    op.drop_table('review_upvoters')
    op.drop_table('reviews')
    op.drop_table('mods')
    op.drop_table('connections')
    op.drop_table('reports')

    op.drop_constraint('fk_editors_choice_author_id_users', 'editors_choice', type_='foreignkey')
    op.drop_constraint('fk_editors_choice_mod_id_mods', 'editors_choice', type_='foreignkey')
    op.create_foreign_key(op.f('fk_editors_choice_author_id_user'), 'editors_choice', 'user', ['author_id'], ['id'])
    op.create_foreign_key(op.f('fk_editors_choice_mod_id_mod'), 'editors_choice', 'mod', ['mod_id'], ['id'])
    op.drop_constraint('fk_media_mod_id_mods', 'media', type_='foreignkey')
    op.create_foreign_key(op.f('fk_media_mod_id_mod'), 'media', 'mod', ['mod_id'], ['id'])


def downgrade():
    op.drop_constraint(op.f('fk_media_mod_id_mod'), 'media', type_='foreignkey')
    op.create_foreign_key('fk_media_mod_id_mods', 'media', 'mods', ['mod_id'], ['id'])
    op.drop_constraint(op.f('fk_editors_choice_mod_id_mod'), 'editors_choice', type_='foreignkey')
    op.drop_constraint(op.f('fk_editors_choice_author_id_user'), 'editors_choice', type_='foreignkey')
    op.create_foreign_key('fk_editors_choice_mod_id_mods', 'editors_choice', 'mods', ['mod_id'], ['id'])
    op.create_foreign_key('fk_editors_choice_author_id_users', 'editors_choice', 'users', ['author_id'], ['id'])

    op.create_table('reports',
        sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('content', sa.VARCHAR(length=1000), autoincrement=False, nullable=True),
        sa.Column('author_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('mod_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('type', postgresql.ENUM('ipg_violation', 'conduct_violation', 'dmca', name='reporttype'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='fk_reports_author_id_users'),
        sa.ForeignKeyConstraint(['mod_id'], ['mods.id'], name='fk_reports_mod_id_mods'),
        sa.PrimaryKeyConstraint('id', name='pk_reports')
    )
    op.create_table('connections',
        sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('type', postgresql.ENUM('github', 'gitlab', 'discord', name='connectiontype'), autoincrement=False, nullable=True),
        sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user'], ['users.id'], name='fk_connections_user_users'),
        sa.PrimaryKeyConstraint('id', name='pk_connections')
    )
    op.create_table('mods',
        sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('title', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column('icon', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('banner', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('tagline', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('description', sa.VARCHAR(length=10000), autoincrement=False, nullable=True),
        sa.Column('website', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('is_private_beta', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('category', postgresql.ENUM('unassigned', 'tools', 'comedy', 'tragic_comedy', 'drama', 'rom_com', 'romance', 'horror', 'mystery', 'satire', 'thriller', 'sci_fi', name='modcategory'), autoincrement=False, nullable=True),
        sa.Column('nsfw', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('released_at', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('last_updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('status', postgresql.ENUM('archived', 'planning', 'in_development', 'playtesting', 'released', name='modstatus'), autoincrement=False, nullable=True),
        sa.Column('downloads', sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column('download_url', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('theme_color', postgresql.ENUM('default', 'red', 'pink', 'purple', 'deep_purple', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange', 'deep_orange', name='modcolor'), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_mods'),
        sa.UniqueConstraint('title', name='uq_mods_title'),
        postgresql_ignore_search_path=False
    )
    op.create_table('reviews',
        sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('rating', sa.NUMERIC(), autoincrement=False, nullable=True),
        sa.Column('content', sa.VARCHAR(length=2000), autoincrement=False, nullable=True),
        sa.Column('mod_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('author_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('title', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], name='fk_reviews_author_id_users'),
        sa.ForeignKeyConstraint(['mod_id'], ['mods.id'], name='fk_reviews_mod_id_mods'),
        sa.PrimaryKeyConstraint('id', name='pk_reviews'),
        postgresql_ignore_search_path=False
    )
    op.create_table('review_upvoters',
        sa.Column('review_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], name='fk_review_upvoters_review_id_reviews'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_review_upvoters_user_id_users')
    )
    op.create_table('users',
        sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('username', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
        sa.Column('avatar', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('bio', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('supporter', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('developer', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('moderator', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('editor', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('email_verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('password', postgresql.BYTEA(), autoincrement=False, nullable=True),
        sa.Column('last_pass_reset', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username'),
        postgresql_ignore_search_path=False
    )
    op.create_table('review_downvoters',
        sa.Column('review_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], name='fk_review_downvoters_review_id_reviews'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_review_downvoters_user_id_users')
    )
    op.create_table('user_favourites',
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('mod_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mods.id'], name='fk_user_favourites_mod_id_mods'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_favourites_user_id_users')
    )
    op.create_table('mod_playtesters',
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('mod_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mods.id'], name='fk_mod_playtesters_mod_id_mods'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_mod_playtesters_user_id_users')
    )
    op.create_table('review_funnys',
        sa.Column('review_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], name='fk_review_helpfuls_review_id_reviews'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_review_helpfuls_user_id_users')
    )
    op.create_table('user_mods',
        sa.Column('role', postgresql.ENUM('unassigned', 'owner', 'co_owner', 'programmer', 'artist', 'writer', 'musician', 'public_relations', name='authorrole'), autoincrement=False, nullable=True),
        sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('mod_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mods.id'], name='fk_user_mods_mod_id_mods'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_mods_user_id_users')
    )

    op.drop_table('review_reaction')
    op.drop_table('user_mod')
    op.drop_table('user_favorite')
    op.drop_table('review')
    op.drop_table('report')
    op.drop_table('mod_playtester')
    op.drop_table('connection')
    op.drop_table('user')
    op.drop_table('mod')
