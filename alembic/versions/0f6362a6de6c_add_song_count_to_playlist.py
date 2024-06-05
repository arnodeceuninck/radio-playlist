"""Add song_count to Playlist

Revision ID: 0f6362a6de6c
Revises: e69426cdc3d4
Create Date: 2024-06-05 22:44:16.473664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f6362a6de6c'
down_revision: Union[str, None] = 'e69426cdc3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('playlist', sa.Column('song_count', sa.Integer(), nullable=False, server_default='0'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('playlist', 'song_count')
    # ### end Alembic commands ###
