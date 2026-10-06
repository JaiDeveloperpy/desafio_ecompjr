from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"
    # Última barreira contra estoque negativo: mesmo que algum código esqueça
    # de validar, o próprio banco recusa a gravação.
    __table_args__ = (
        CheckConstraint("quantidade_em_estoque >= 0", name="ck_produtos_estoque_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    # Numeric em vez de float: dinheiro não pode sofrer erro de arredondamento.
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantidade_em_estoque: Mapped[int] = mapped_column(default=0)
    estoque_minimo: Mapped[int] = mapped_column(default=0)
    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # RESTRICT: o banco impede apagar categoria/fornecedor que ainda tenha produtos.
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="RESTRICT"))
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id", ondelete="RESTRICT"))
