"""remove image width and height

Revision ID: bfeeab0247d3
Revises: 666038eed4e9
Create Date: 2024-03-27 14:55:24.374828

"""
import sqlmodel
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfeeab0247d3'
down_revision: Union[str, None] = '666038eed4e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dataimage', 'width')
    op.drop_column('dataimage', 'height')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dataimage', sa.Column('height', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('dataimage', sa.Column('width', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
