"""cria tabela denuncias

Revision ID: 77b22e49f7ff
Revises: ab3184e95c70
Create Date: 2026-11-13 01:38:05.040986

"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77b22e49f7ff'
down_revision: Union[str, Sequence[str], None] = 'ab3184e95c70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('denuncias',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_denunciante', sa.Integer(), nullable=False),
    sa.Column('id_grupo', sa.Integer(), nullable=False),
    sa.Column('id_conteudo', sa.Integer(), nullable=True),
    sa.Column('motivo', sa.String(length=30), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), server_default='pendente', nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('resolvido_em', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['id_conteudo'], ['conteudos.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['id_denunciante'], ['usuarios.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_grupo'], ['grupos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_denuncias_id_denunciante'), 'denuncias', ['id_denunciante'], unique=False)
    op.create_index(op.f('ix_denuncias_id_grupo'), 'denuncias', ['id_grupo'], unique=False)
    op.create_index(op.f('ix_denuncias_status'), 'denuncias', ['status'], unique=False)
    
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_denuncias_status'), table_name='denuncias')
    op.drop_index(op.f('ix_denuncias_id_grupo'), table_name='denuncias')
    op.drop_index(op.f('ix_denuncias_id_denunciante'), table_name='denuncias')
    op.drop_table('denuncias')
    # ### end Alembic commands ###
