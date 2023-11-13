"""Added gallery model

Revision ID: 3769c1540693
Revises: 4cde84bafa95
Create Date: 2023-11-12 20:46:25.511946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3769c1540693'
down_revision = '4cde84bafa95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('galleries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('galleries')
    # ### end Alembic commands ###