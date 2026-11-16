"""trigger de auditoria nas tabelas que faltam

Revision ID: ee7084bf0477
Revises: 3ba959894064
Create Date: 2026-11-16 01:18:31.674117

"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee7084bf0477'
down_revision: Union[str, Sequence[str], None] = '3ba959894064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# so acao de staff e o que tem peso
TABELAS = [
    "documentos_legais",
    "aceites_documentos_legais",
    "denuncias",
    "avisos",
    "grupos",
]


def upgrade() -> None:
    """Upgrade schema."""
    for tabela in TABELAS:
        op.execute(f"""
            CREATE TRIGGER {tabela}_auditoria
            AFTER INSERT OR UPDATE OR DELETE ON {tabela}
            FOR EACH ROW EXECUTE FUNCTION registrar_auditoria();
        """)


def downgrade() -> None:
    """Downgrade schema."""
    for tabela in TABELAS:
        op.execute(f"DROP TRIGGER {tabela}_auditoria ON {tabela};")
