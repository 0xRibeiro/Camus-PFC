"""junta as heads de moderacao e iot

Revision ID: 29dd7a875458
Revises: 031360c8e0fc, b8ffe123f654
Create Date: 2026-11-14 22:56:47.475308

"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29dd7a875458'
down_revision: Union[str, Sequence[str], None] = ('031360c8e0fc', 'b8ffe123f654')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
