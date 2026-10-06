from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.schemas.erro import respostas_erro
from app.security import exigir_admin, usuario_atual
from app.services import categoria as service

router = APIRouter(
    prefix="/categorias", tags=["Categorias"],
    dependencies=[Depends(usuario_atual)],
    responses=respostas_erro(401),
)


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
    responses=respostas_erro(400, 403, 409),
    dependencies=[Depends(exigir_admin)],
)
def criar(dados: CategoriaCreate, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Atualiza parcialmente uma categoria",
    responses=respostas_erro(400, 403, 404, 409),
    dependencies=[Depends(exigir_admin)],
)
def atualizar(categoria_id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    return service.atualizar(db, categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma categoria sem produtos vinculados",
    responses=respostas_erro(403, 404, 409),
    dependencies=[Depends(exigir_admin)],
)
def excluir(categoria_id: int, db: Session = Depends(get_db)):
    service.excluir(db, categoria_id)
