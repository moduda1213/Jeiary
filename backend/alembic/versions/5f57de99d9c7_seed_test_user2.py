"""seed_test_user2

Revision ID: 5f57de99d9c7
Revises: be1e711475b4
Create Date: 2025-11-10 17:14:46.074884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.core.security import get_password_hash

# revision identifiers, used by Alembic.
revision: str = '5f57de99d9c7'
down_revision: Union[str, None] = 'be1e711475b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users_table = sa.table('users',
        sa.column('email', sa.String),
        sa.column('password_hash', sa.String)
    )
    
    op.bulk_insert(users_table,
        [
            {'email': 'test2@example.com', 'password_hash': get_password_hash('password123@')}
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'test2@example.com'")