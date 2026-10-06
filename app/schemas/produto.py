from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# quantidade_em_estoque não entra no Create nem no Update de propósito:
# o estoque só muda por Movimentação, assim todo ajuste fica no histórico de auditoria.

class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120, examples=["Luminária de papel"])
    sku: str = Field(min_length=1, max_length=50, examples=["LUM-001"])
    preco_custo: Decimal = Field(ge=0, max_digits=10, decimal_places=2, examples=["12.50"])
    preco_venda: Decimal = Field(ge=0, max_digits=10, decimal_places=2, examples=["29.90"])
    estoque_minimo: int = Field(default=0, ge=0, examples=[5])
    categoria_id: int
    fornecedor_id: int

class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    preco_custo: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    preco_venda: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    estoque_minimo: int | None = Field(default=None, ge=0)
    categoria_id: int | None = None
    fornecedor_id: int | None = None

class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    sku: str
    preco_custo: Decimal
    preco_venda: Decimal
    quantidade_em_estoque: int
    estoque_minimo: int
    data_cadastro: datetime
    categoria_id: int
    fornecedor_id: int
