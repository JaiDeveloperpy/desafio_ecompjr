from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import Conflito, NaoEncontrado
from app.models import Categoria, Produto
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


def listar(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.id)))


def buscar(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NaoEncontrado(f"Categoria {categoria_id} não encontrada.")
    return categoria


def _garantir_nome_livre(db: Session, nome: str, ignorar_id: int | None = None) -> None:
    existente = db.scalar(select(Categoria).where(Categoria.nome == nome))
    if existente is not None and existente.id != ignorar_id:
        raise Conflito(f"Já existe uma categoria com o nome '{nome}'.")


def criar(db: Session, dados: CategoriaCreate) -> Categoria:
    _garantir_nome_livre(db, dados.nome)
    categoria = Categoria(**dados.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def atualizar(db: Session, categoria_id: int, dados: CategoriaUpdate) -> Categoria:
    categoria = buscar(db, categoria_id)
    # exclude_none: no PATCH, campo omitido (ou null) significa "não mexer".
    alteracoes = dados.model_dump(exclude_none=True)
    if "nome" in alteracoes:
        _garantir_nome_livre(db, alteracoes["nome"], ignorar_id=categoria_id)
    for campo, valor in alteracoes.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def excluir(db: Session, categoria_id: int) -> None:
    categoria = buscar(db, categoria_id)
    # Bloqueia em vez de apagar em cascata: sumir com produtos (e o histórico
    # de estoque deles) por causa de uma categoria seria perda de dados.
    if db.scalar(select(Produto.id).where(Produto.categoria_id == categoria_id).limit(1)):
        raise Conflito("A categoria possui produtos vinculados e não pode ser excluída.")
    db.delete(categoria)
    db.commit()
