from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.erro import respostas_erro
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from app.services import produto as service

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProdutoResponse], summary="Lista os produtos com filtros opcionais")
def listar(
    categoria_id: int | None = None,
    fornecedor_id: int | None = None,
    nome: str | None = None,
    db: Session = Depends(get_db),
):
    return service.listar(db, categoria_id, fornecedor_id, nome)


# Precisa vir antes de "/{produto_id}": as rotas são testadas na ordem em que
# são declaradas, e "estoque-baixo" seria lido como um id inválido.
@router.get(
    "/estoque-baixo",
    response_model=list[ProdutoResponse],
    summary="Lista produtos com estoque no mínimo ou abaixo dele",
)
def estoque_baixo(db: Session = Depends(get_db)):
    return service.listar_estoque_baixo(db)


@router.get(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Busca um produto pelo id",
    responses=respostas_erro(404),
)
def buscar(produto_id: int, db: Session = Depends(get_db)):
    return service.buscar(db, produto_id)


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um produto (estoque inicial 0; use movimentações para dar entrada)",
    responses=respostas_erro(400, 404, 409),
)
def criar(dados: ProdutoCreate, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.patch(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualiza parcialmente um produto (o estoque só muda por movimentação)",
    responses=respostas_erro(400, 404, 409),
)
def atualizar(produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    return service.atualizar(db, produto_id, dados)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um produto sem movimentações registradas",
    responses=respostas_erro(404, 409),
)
def excluir(produto_id: int, db: Session = Depends(get_db)):
    service.excluir(db, produto_id)
