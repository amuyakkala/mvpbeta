"""add status to traces

Revision ID: 89f649b8c3a8
Revises: 21bc00466e79
Create Date: 2024-04-28 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89f649b8c3a8'
down_revision = '21bc00466e79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status column to traces table
    op.add_column('traces', sa.Column('status', sa.String(), nullable=True, server_default='pending'))


def downgrade() -> None:
    # Remove status column from traces table
    op.drop_column('traces', 'status') 