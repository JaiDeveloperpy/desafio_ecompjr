import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"

class Movimentacao(Base):
    # Registro de auditoria: só é criado e consultado, nunca editado nem apagado.
    __tablename__ = "movimentacoes"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_movimentacoes_quantidade_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoMovimentacao] = mapped_column(Enum(TipoMovimentacao, name="tipo_movimentacao"))
    quantidade: Mapped[int]
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # RESTRICT: um produto com histórico não pode sumir, senão a auditoria perde a referência.
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id", ondelete="RESTRICT"))
