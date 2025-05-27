"""add foreign key to post table

Revision ID: 67951f4a479d
Revises: 1d92a86d019e
Create Date: 2025-05-26 08:47:40.765663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67951f4a479d'
down_revision = '1d92a86d019e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'osts_users_fk',  # name of the foreign key constraint
        'posts',           # source table
        'users',           # referent table
        ['owner_id'],      # source column(s)
        ['id'],            # referent column(s)
        ondelete='CASCADE' # action on delete
    )
    pass


def downgrade() -> None:
    op.drop_constraint('osts_users_fk', 'posts', type_='foreignkey')
    op.drop_column('posts', 'owner_id')
    pass
