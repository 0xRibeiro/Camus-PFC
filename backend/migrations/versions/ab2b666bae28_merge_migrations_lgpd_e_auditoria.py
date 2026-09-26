"""merge migrations lgpd e auditoria

Revision ID: ab2b666bae28
Revises: c6f85c27d30e, e1930ec7d5c6
Create Date: 2026-09-26 01:08:01.196857

"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab2b666bae28'
down_revision: Union[str, Sequence[str], None] = ('c6f85c27d30e', 'e1930ec7d5c6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
