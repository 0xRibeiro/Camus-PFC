"""junta as cabeca 2

Revision ID: 48d50f55f2c3
Revises: ab3184e95c70, e1a0468314eb
Create Date: 2026-11-12 19:50:36.311129

"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48d50f55f2c3'
down_revision: Union[str, Sequence[str], None] = ('ab3184e95c70', 'e1a0468314eb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
