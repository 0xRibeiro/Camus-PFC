from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# motivo e status são só texto no banco, sem enum do postgres. quem confere os valores
# aceitos é o schema (Literal), então não tem migration de enum pra lidar.
STATUS_PENDENTE = "pendente"


## toda denúncia nasce dentro de um grupo. com id_conteudo ela aponta pra um conteúdo
## daquele grupo; sem ele, o alvo é o próprio grupo (ou seja, o dono).
class Denuncia(Base):
    __tablename__ = "denuncias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    id_denunciante: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)

    id_grupo: Mapped[int] = mapped_column(ForeignKey("grupos.id", ondelete="CASCADE"), index=True)

    # o dono pode apagar o conteúdo, mas a denúncia continua registrada (o campo vira null)
    id_conteudo: Mapped[int | None] = mapped_column(ForeignKey("conteudos.id", ondelete="SET NULL"))

    motivo: Mapped[str] = mapped_column(String(30))

    descricao: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default=STATUS_PENDENTE, server_default=STATUS_PENDENTE, index=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))