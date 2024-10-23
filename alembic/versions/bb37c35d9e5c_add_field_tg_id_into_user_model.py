"""add field tg_id into user model

Revision ID: bb37c35d9e5c
Revises: f71f3f6de2f8
Create Date: 2024-10-23 07:56:41.106833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb37c35d9e5c'
down_revision: Union[str, None] = 'f71f3f6de2f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('tg_id', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'tg_id')
    # ### end Alembic commands ###
