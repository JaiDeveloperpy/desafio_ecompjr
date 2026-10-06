from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TipoMovimentacao
from app.schemas.erro import respostas_erro
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse
from app.services import movimentacao as service

# Só GET e POST: movimentação é histórico de auditoria, então não há rota de
# edição nem de exclusão (PUT/PATCH/DELETE respondem 405).
router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])


@router.get(
    "",
    response_model=list[MovimentacaoResponse],
    summary="Lista o histórico com filtros por período, fornecedor, produto e tipo",
    responses=respostas_erro(400),
)
def listar(
    produto_id: int | None = None,
    fornecedor_id: int | None = None,
    tipo: TipoMovimentacao | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
):
    return service.listar(db, produto_id, fornecedor_id, tipo, data_inicio, data_fim)


@router.get(
    "/{movimentacao_id}",
    response_model=MovimentacaoResponse,
    summary="Busca uma movimentação pelo id",
    responses=respostas_erro(404),
)
def buscar(movimentacao_id: int, db: Session = Depends(get_db)):
    return service.buscar(db, movimentacao_id)


@router.post(
    "",
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra entrada ou saída e atualiza o estoque do produto",
    responses=respostas_erro(400, 404),
)
def registrar(dados: MovimentacaoCreate, db: Session = Depends(get_db)):
    return service.registrar(db, dados)
