"""Add full_name to users table

Revision ID: 20240319_add_full_name
Revises: 20240319_initial_migration
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240319_add_full_name'
down_revision = '20240319_initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Add full_name column to users table
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

def downgrade():
    # Remove full_name column from users table
    op.drop_column('users', 'full_name') 