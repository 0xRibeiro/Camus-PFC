"""trigger para audit

Revision ID: c6f85c27d30e
Revises: e38ff668d53d
Create Date: 2026-09-25 07:33:32.696410

"""
from typing import Sequence, Union


from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c6f85c27d30e'
down_revision: Union[str, Sequence[str], None] = 'e38ff668d53d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION registrar_auditoria() RETURNS trigger AS $$
        DECLARE
            usuario int;
            acao_texto text;
            antigo jsonb;
            novo jsonb;
            id_afetado int;
        BEGIN
            usuario := NULLIF(current_setting('app.current_user_id', true), '')::int;

            IF TG_OP = 'INSERT' THEN
                acao_texto := 'create';
                antigo := null;
                novo := to_jsonb(NEW);
                id_afetado := NEW.id;
            END IF;

            IF TG_OP = 'UPDATE' THEN
                acao_texto := 'update';
                antigo := to_jsonb(OLD);
                novo := to_jsonb(NEW);
                id_afetado := NEW.id;
            END IF;

            IF TG_OP = 'DELETE' THEN
                acao_texto := 'delete';
                antigo := to_jsonb(OLD);
                novo := null;
                id_afetado := OLD.id;
            END IF;

            INSERT INTO logs_auditoria (usuario_id, acao, entidade, entidade_id, alteracoes, criado_em)
            VALUES (usuario, acao_texto::acaoauditoria, TG_TABLE_NAME, id_afetado, jsonb_build_object('antigo', antigo, 'novo', novo), now());

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    tabelas_auditadas = [
        "usuarios",
        "trilhas",
        "modulos",
        "conteudos",
        "questoes",
        "alternativas",
        "conquistas",
    ]

    for tabela in tabelas_auditadas:
        op.execute(f"""
            CREATE TRIGGER {tabela}_auditoria
            AFTER INSERT OR UPDATE OR DELETE ON {tabela}
            FOR EACH ROW EXECUTE FUNCTION registrar_auditoria();
        """)


def downgrade() -> None:
    """Downgrade schema."""
    tabelas_auditadas = [
        "usuarios",
        "trilhas",
        "modulos",
        "conteudos",
        "questoes",
        "alternativas",
        "conquistas",
    ]

    for tabela in tabelas_auditadas:
        op.execute(f"DROP TRIGGER {tabela}_auditoria ON {tabela};")

    op.execute("DROP FUNCTION registrar_auditoria();")
