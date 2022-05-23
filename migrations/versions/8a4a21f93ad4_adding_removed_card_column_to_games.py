"""adding removed_card column to games

Revision ID: 8a4a21f93ad4
Revises: 8f16dc4b130d
Create Date: 2022-05-23 12:26:03.182580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a4a21f93ad4'
down_revision = '8f16dc4b130d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('removed_card', sa.Enum('WILD', 'PLUS_TWO', 'RAT', 'RABBIT', 'SNAKE', 'SHEEP', 'MONKEY', 'CHICKEN', 'DOG', name='cardtype'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'removed_card')
    # ### end Alembic commands ###
