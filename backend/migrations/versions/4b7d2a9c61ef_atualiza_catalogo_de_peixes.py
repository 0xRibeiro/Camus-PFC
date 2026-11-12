"""Atualiza o catálogo de peixes."""

from alembic import op

revision = "4b7d2a9c61ef"
down_revision = "e50f5dd7881e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("especie_peixe", "peixes", type_="check")
    op.create_check_constraint(
        "especie_peixe",
        "peixes",
        "especie IN ('DOURADO', 'BETTA', 'PALHACO', 'ANJO', 'NEON', "
        "'CHROMIS', 'BANGGAI', 'ANTHIAS', 'BODIAO')",
    )


def downgrade() -> None:
    op.drop_constraint("especie_peixe", "peixes", type_="check")
    op.create_check_constraint(
        "especie_peixe",
        "peixes",
        "especie IN ('CHROMIS', 'PALHACO', 'BANGGAI', 'ANTHIAS', 'BODIAO')",
    )