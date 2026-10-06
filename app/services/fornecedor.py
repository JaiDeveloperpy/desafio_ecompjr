from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import Conflito, NaoEncontrado
from app.models import Fornecedor, Produto
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate


def listar(db: Session) -> list[Fornecedor]:
    return list(db.scalars(select(Fornecedor).order_by(Fornecedor.id)))


def buscar(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if fornecedor is None:
        raise NaoEncontrado(f"Fornecedor {fornecedor_id} não encontrado.")
    return fornecedor


def _garantir_unicos(db: Session, dados: dict, ignorar_id: int | None = None) -> None:
    for campo in ("cnpj", "email"):
        if campo not in dados:
            continue
        existente = db.scalar(
            select(Fornecedor).where(getattr(Fornecedor, campo) == dados[campo])
        )
        if existente is not None and existente.id != ignorar_id:
            raise Conflito(f"Já existe um fornecedor com este {campo}.")


def criar(db: Session, dados: FornecedorCreate) -> Fornecedor:
    valores = dados.model_dump()
    _garantir_unicos(db, valores)
    fornecedor = Fornecedor(**valores)
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def atualizar(db: Session, fornecedor_id: int, dados: FornecedorUpdate) -> Fornecedor:
    fornecedor = buscar(db, fornecedor_id)
    alteracoes = dados.model_dump(exclude_none=True)
    _garantir_unicos(db, alteracoes, ignorar_id=fornecedor_id)
    for campo, valor in alteracoes.items():
        setattr(fornecedor, campo, valor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def excluir(db: Session, fornecedor_id: int) -> None:
    fornecedor = buscar(db, fornecedor_id)
    if db.scalar(select(Produto.id).where(Produto.fornecedor_id == fornecedor_id).limit(1)):
        raise Conflito("O fornecedor possui produtos vinculados e não pode ser excluído.")
    db.delete(fornecedor)
    db.commit()
