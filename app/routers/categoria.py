from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.schemas.erro import respostas_erro
from app.services import categoria as service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoriaResponse], summary="Lista as categorias")
def listar(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Busca uma categoria pelo id",
    responses=respostas_erro(404),
)
def buscar(categoria_id: int, db: Session = Depends(get_db)):
    return service.buscar(db, categoria_id)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma categoria",
    responses=respostas_erro(400, 409),
)
def criar(dados: CategoriaCreate, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Atualiza parcialmente uma categoria",
    responses=respostas_erro(400, 404, 409),
)
def atualizar(categoria_id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    return service.atualizar(db, categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma categoria sem produtos vinculados",
    responses=respostas_erro(404, 409),
)
def excluir(categoria_id: int, db: Session = Depends(get_db)):
    service.excluir(db, categoria_id)
