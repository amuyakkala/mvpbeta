"""Update user model to use full_name

Revision ID: 20240319_update_user_model
Revises: 20240319_add_full_name
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240319_update_user_model'
down_revision = '20240319_add_full_name'
branch_labels = None
depends_on = None

def upgrade():
    # Drop first_name and last_name columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
    
    # Make full_name not nullable
    op.alter_column('users', 'full_name', nullable=False)

def downgrade():
    # Add back first_name and last_name columns
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    
    # Make full_name nullable again
    op.alter_column('users', 'full_name', nullable=True) 