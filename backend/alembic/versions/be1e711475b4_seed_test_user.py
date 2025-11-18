"""seed_test_user

Revision ID: be1e711475b4
Revises: 95d25bf30d62
Create Date: 2025-11-10 15:46:45.424178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.core.security import get_password_hash

# revision identifiers, used by Alembic.
revision: str = 'be1e711475b4'
down_revision: Union[str, None] = '95d25bf30d62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users_table = sa.table('users',
        sa.column('email', sa.String),
        sa.column('password_hash', sa.String)
    )
    
    op.bulk_insert(users_table,
        [
            {'email': 'test@example.com', 'password_hash': get_password_hash('password123@')}
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'test@example.com'")
