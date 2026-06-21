"""Add hashed_password to users

Revision ID: e6199ffc5431
Revises: e13325709620
Create Date: 2026-06-21 23:00:44.505367

"""
from typing import Sequence, Union

from alembic import op # pyrefly: ignore [missing-import]
import sqlalchemy as sa # pyrefly: ignore [missing-import]


# revision identifiers, used by Alembic.
revision: str = 'e6199ffc5431'
down_revision: Union[str, Sequence[str], None] = 'e13325709620'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False, server_default=''))
    op.alter_column("users", "hashed_password",server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hashed_password')
