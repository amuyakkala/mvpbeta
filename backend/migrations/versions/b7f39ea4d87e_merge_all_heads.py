"""merge all heads

Revision ID: b7f39ea4d87e
Revises: 20240319_update_user_model, c6280f5be72f, initial_migration
Create Date: 2025-04-28 21:16:19.449449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7f39ea4d87e'
down_revision = ('20240319_update_user_model', 'c6280f5be72f', 'initial_migration')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 