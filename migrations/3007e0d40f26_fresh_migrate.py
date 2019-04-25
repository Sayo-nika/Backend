# flake8: noqa: E128
"""
Fresh migrate

Revision ID: 3007e0d40f26
Revises:
Create Date: 2019-04-25 09:59:15.435631+00:00
"""
# External Libraries
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3007e0d40f26'
down_revision = None
branch_labels = None
depends_on = None

enums = {
    'mod_category': sa.Enum('unassigned', 'tools', 'comedy', 'tragic_comedy', 'drama', 'rom_com', 'romance', 'horror', 'mystery', 'satire', 'thriller', 'sci_fi', name='modcategory'),
    'mod_color': sa.Enum('default', 'red', 'pink', 'purple', 'deep_purple', 'indigo', 'blue', 'cyan', 'teal', 'green', 'lime', 'yellow', 'orange', 'deep_orange', name='modcolor'),
    'mod_status': sa.Enum('archived', 'planning', 'in_development', 'playtesting', 'released', name='modstatus'),
    'connection_type': sa.Enum('github', 'gitlab', 'discord', name='connectiontype'),
    'media_type': sa.Enum('image', 'video', name='mediatype'),
    'report_type': sa.Enum('ipg_violation', 'conduct_violation', 'dmca', name='reporttype'),
    'author_role': sa.Enum('unassigned', 'owner', 'co_owner', 'programmer', 'artist', 'writer', 'musician', 'public_relations', name='authorrole'),
    'reaction_type': sa.Enum('upvote', 'downvote', 'funny', name='reactiontype')
}


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
        sa.Column('category', enums['mod_category'], nullable=True),
        sa.Column('nsfw', sa.Boolean(), nullable=True),
        sa.Column('theme_color', enums['mod_color'], nullable=True),
        sa.Column('released_at', sa.Date(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('status', enums['mod_status'], nullable=True),
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
        sa.Column('type', enums['connection_type'], nullable=True),
        sa.Column('user', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['user'], ['user.id'], name=op.f('fk_connection_user_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_connection'))
    )
    op.create_table('editors_choice',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.Column('featured', sa.Boolean(), nullable=True),
        sa.Column('editors_notes', sa.Unicode(length=500), nullable=True),
        sa.Column('author_id', sa.Unicode(), nullable=True),
        sa.Column('article_url', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], name=op.f('fk_editors_choice_author_id_user')),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_editors_choice_mod_id_mod')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_editors_choice'))
    )
    op.create_table('media',
        sa.Column('id', sa.Unicode(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('type', enums['media_type'], nullable=True),
        sa.Column('url', sa.Unicode(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_media_mod_id_mod')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_media'))
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
        sa.Column('type', enums['report_type'], nullable=True),
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
        sa.Column('role', enums['author_role'], nullable=True),
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('mod_id', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['mod_id'], ['mod.id'], name=op.f('fk_user_mod_mod_id_mod')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_mod_user_id_user'))
    )
    op.create_table('review_reaction',
        sa.Column('review_id', sa.Unicode(), nullable=True),
        sa.Column('user_id', sa.Unicode(), nullable=True),
        sa.Column('reaction', enums['reaction_type'], nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['review.id'], name=op.f('fk_review_reaction_review_id_review')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_review_reaction_user_id_user'))
    )


def downgrade():
    op.drop_table('review_reaction')
    op.drop_table('user_mod')
    op.drop_table('user_favorite')
    op.drop_table('review')
    op.drop_table('report')
    op.drop_table('mod_playtester')
    op.drop_table('media')
    op.drop_table('editors_choice')
    op.drop_table('connection')
    op.drop_table('user')
    op.drop_table('mod')

    op_bind = op.get_bind()

    for enum in enums.values():
        enum.drop(op_bind, checkfirst=False)
