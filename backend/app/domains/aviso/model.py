from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


## Recado que o admin manda pro usuário quando mexe num grupo dele (suspende, reativa
## ou exclui). Tem tabela própria porque, se o grupo for excluído, ele não existe mais.
class Aviso(Base):
    __tablename__ = "avisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)

    mensagem: Mapped[str] = mapped_column(Text)

    # vira true quando o usuário clica em "entendi"
    lido: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), index=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())