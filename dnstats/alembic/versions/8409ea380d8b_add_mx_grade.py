"""Add MX grade

Revision ID: 8409ea380d8b
Revises: b0a3da6447a1
Create Date: 2021-03-18 21:30:20.844737

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8409ea380d8b'
down_revision = 'b0a3da6447a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('site_runs', sa.Column('mx_grade', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('site_runs', 'mx_grade')
    # ### end Alembic commands ###
