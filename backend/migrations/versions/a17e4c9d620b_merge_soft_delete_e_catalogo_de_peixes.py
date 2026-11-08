
    
  
"""merge soft delete e catalogo de peixes

Revision ID: a17e4c9d620b
Revises: 5451535b2b9c, 4b7d2a9c61ef
Create Date: 2026-11-08 15:11:57.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'a17e4c9d620b'
down_revision: Union[str, Sequence[str], None] = ('5451535b2b9c', '4b7d2a9c61ef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass