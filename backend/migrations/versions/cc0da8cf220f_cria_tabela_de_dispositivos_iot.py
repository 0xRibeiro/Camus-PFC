"""cria tabela de dispositivos iot

Revision ID: cc0da8cf220f
Revises: 147401a9a496
Create Date: 2026-11-07 16:34:14.225814

"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc0da8cf220f'
down_revision: Union[str, Sequence[str], None] = '147401a9a496'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # tabela dispositivos agora eh criada na 28107fa48fbd (domain dispositivo)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
