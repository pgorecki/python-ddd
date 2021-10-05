"""initial listing model

Revision ID: d6c2334f4816
Revises: 
Create Date: 2021-09-27 17:33:02.166128

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd6c2334f4816'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catalog_listing',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('catalog_listing')
    # ### end Alembic commands ###
