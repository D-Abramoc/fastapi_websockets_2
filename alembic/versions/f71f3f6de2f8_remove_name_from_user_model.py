"""remove name from user model

Revision ID: f71f3f6de2f8
Revises: e74a8f4ba379
Create Date: 2024-10-22 11:41:00.477209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f71f3f6de2f8'
down_revision: Union[str, None] = 'e74a8f4ba379'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
