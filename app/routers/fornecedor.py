from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.erro import respostas_erro
from app.security import exigir_admin, usuario_atual
from app.schemas.fornecedor import FornecedorCreate, FornecedorResponse, FornecedorUpdate
from app.services import fornecedor as service

router = APIRouter(
    prefix="/fornecedores", tags=["Fornecedores"],
    dependencies=[Depends(usuario_atual)],
    responses=respostas_erro(401),
)


@router.get("", response_model=list[FornecedorResponse], summary="Lista os fornecedores")
def listar(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get(
    "/{fornecedor_id}",
    response_model=FornecedorResponse,
    summary="Busca um fornecedor pelo id",
    responses=respostas_erro(404),
)
def buscar(fornecedor_id: int, db: Session = Depends(get_db)):
    return service.buscar(db, fornecedor_id)


@router.post(
    "",
    response_model=FornecedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um fornecedor",
    responses=respostas_erro(400, 403, 409),
    dependencies=[Depends(exigir_admin)],
)
def criar(dados: FornecedorCreate, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.patch(
    "/{fornecedor_id}",
    response_model=FornecedorResponse,
    summary="Atualiza parcialmente um fornecedor",
    responses=respostas_erro(400, 403, 404, 409),
    dependencies=[Depends(exigir_admin)],
)
def atualizar(fornecedor_id: int, dados: FornecedorUpdate, db: Session = Depends(get_db)):
    return service.atualizar(db, fornecedor_id, dados)


@router.delete(
    "/{fornecedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um fornecedor sem produtos vinculados",
    responses=respostas_erro(403, 404, 409),
    dependencies=[Depends(exigir_admin)],
)
def excluir(fornecedor_id: int, db: Session = Depends(get_db)):
    service.excluir(db, fornecedor_id)
