from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import Conflito, NaoEncontrado
from app.models import Movimentacao, Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from app.services import categoria as categoria_service
from app.services import fornecedor as fornecedor_service


def listar(
    db: Session,
    categoria_id: int | None = None,
    fornecedor_id: int | None = None,
    nome: str | None = None,
) -> list[Produto]:
    consulta = select(Produto).order_by(Produto.id)
    if categoria_id is not None:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    if fornecedor_id is not None:
        consulta = consulta.where(Produto.fornecedor_id == fornecedor_id)
    if nome:
        consulta = consulta.where(Produto.nome.ilike(f"%{nome}%"))
    return list(db.scalars(consulta))


def listar_estoque_baixo(db: Session) -> list[Produto]:
    # Compara duas colunas da mesma linha direto no SQL, sem trazer todos os
    # produtos para o Python. "<=" porque atingir o mínimo já pede reposição.
    consulta = (
        select(Produto)
        .where(Produto.quantidade_em_estoque <= Produto.estoque_minimo)
        .order_by(Produto.quantidade_em_estoque)
    )
    return list(db.scalars(consulta))


def buscar(db: Session, produto_id: int) -> Produto:
    produto = db.get(Produto, produto_id)
    if produto is None:
        raise NaoEncontrado(f"Produto {produto_id} não encontrado.")
    return produto


def _validar_vinculos(db: Session, dados: dict, ignorar_id: int | None = None) -> None:
    # Confere antes de gravar para devolver 404 com mensagem clara, em vez do
    # erro genérico de chave estrangeira do banco.
    if "categoria_id" in dados:
        categoria_service.buscar(db, dados["categoria_id"])
    if "fornecedor_id" in dados:
        fornecedor_service.buscar(db, dados["fornecedor_id"])
    if "sku" in dados:
        existente = db.scalar(select(Produto).where(Produto.sku == dados["sku"]))
        if existente is not None and existente.id != ignorar_id:
            raise Conflito(f"Já existe um produto com o SKU '{dados['sku']}'.")


def criar(db: Session, dados: ProdutoCreate) -> Produto:
    valores = dados.model_dump()
    _validar_vinculos(db, valores)
    produto = Produto(**valores)
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def atualizar(db: Session, produto_id: int, dados: ProdutoUpdate) -> Produto:
    produto = buscar(db, produto_id)
    alteracoes = dados.model_dump(exclude_none=True)
    _validar_vinculos(db, alteracoes, ignorar_id=produto_id)
    for campo, valor in alteracoes.items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


def excluir(db: Session, produto_id: int) -> None:
    produto = buscar(db, produto_id)
    # Produto com movimentações faz parte da auditoria; apagá-lo deixaria
    # registros imutáveis apontando para o nada.
    if db.scalar(select(Movimentacao.id).where(Movimentacao.produto_id == produto_id).limit(1)):
        raise Conflito("O produto possui movimentações registradas e não pode ser excluído.")
    db.delete(produto)
    db.commit()
