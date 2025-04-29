"""update user model

Revision ID: 001
Revises: 
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing columns
    op.drop_column('users', 'username')
    op.drop_column('users', 'role')
    op.drop_column('users', 'meta_data')
    
    # Add new columns
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=False))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=False))

def downgrade():
    # Remove new columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
    
    # Recreate old columns
    op.add_column('users', sa.Column('username', sa.String(), nullable=False))
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False))
    op.add_column('users', sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True)) 