"""vincula trilhas aos grupos

Revision ID: ab3184e95c70
Revises: df6183589578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab3184e95c70'
down_revision: Union[str, Sequence[str], None] = 'df6183589578'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('trilhas', sa.Column('grupo_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_trilhas_grupo_id'), 'trilhas', ['grupo_id'], unique=False)
    op.create_foreign_key(
        'fk_trilhas_grupo_id',
        'trilhas',
        'grupos',
        ['grupo_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove as trilhas privadas antes de perder a informação de escopo.
    op.execute("DELETE FROM trilhas WHERE grupo_id IS NOT NULL")
    op.drop_constraint('fk_trilhas_grupo_id', 'trilhas', type_='foreignkey')
    op.drop_index(op.f('ix_trilhas_grupo_id'), table_name='trilhas')
    op.drop_column('trilhas', 'grupo_id')