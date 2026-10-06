from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.movimentacao import TipoMovimentacao

# Não existe MovimentacaoUpdate: o registro é imutável.

class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0, examples=[10])

class MovimentacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int
    data: datetime
