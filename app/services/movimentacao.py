from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import NaoEncontrado, RegraDeNegocio
from app.models import Movimentacao, Produto, TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoCreate


def listar(
    db: Session,
    produto_id: int | None = None,
    fornecedor_id: int | None = None,
    tipo: TipoMovimentacao | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[Movimentacao]:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise RegraDeNegocio("data_inicio não pode ser posterior a data_fim.")

    consulta = select(Movimentacao).order_by(Movimentacao.data.desc())
    if produto_id is not None:
        consulta = consulta.where(Movimentacao.produto_id == produto_id)
    if fornecedor_id is not None:
        # A movimentação não guarda fornecedor: ele é descoberto pelo produto.
        consulta = consulta.join(Produto).where(Produto.fornecedor_id == fornecedor_id)
    if tipo is not None:
        consulta = consulta.where(Movimentacao.tipo == tipo)
    if data_inicio:
        consulta = consulta.where(Movimentacao.data >= data_inicio)
    if data_fim:
        # "< dia seguinte" para incluir o dia final inteiro (até 23:59:59).
        consulta = consulta.where(Movimentacao.data < data_fim + timedelta(days=1))
    return list(db.scalars(consulta))


def buscar(db: Session, movimentacao_id: int) -> Movimentacao:
    movimentacao = db.get(Movimentacao, movimentacao_id)
    if movimentacao is None:
        raise NaoEncontrado(f"Movimentação {movimentacao_id} não encontrada.")
    return movimentacao


def registrar(db: Session, dados: MovimentacaoCreate) -> Movimentacao:
    # Lock pessimista: SELECT ... FOR UPDATE trava a linha do produto até o
    # commit. Se dois vendedores derem saída no mesmo produto ao mesmo tempo,
    # o segundo espera o primeiro terminar e já lê o estoque atualizado,
    # então nunca os dois "veem" a mesma quantidade e vendem além do que existe.
    produto = db.scalar(
        select(Produto).where(Produto.id == dados.produto_id).with_for_update()
    )
    if produto is None:
        raise NaoEncontrado(f"Produto {dados.produto_id} não encontrado.")

    if dados.tipo == TipoMovimentacao.SAIDA:
        if produto.quantidade_em_estoque < dados.quantidade:
            raise RegraDeNegocio(
                f"Estoque insuficiente: disponível {produto.quantidade_em_estoque}, "
                f"solicitado {dados.quantidade}."
            )
        produto.quantidade_em_estoque -= dados.quantidade
    else:
        produto.quantidade_em_estoque += dados.quantidade

    movimentacao = Movimentacao(**dados.model_dump())
    db.add(movimentacao)
    # Um único commit grava o histórico e o novo estoque juntos (atomicidade):
    # ou os dois acontecem, ou nenhum. Só aqui o lock é liberado.
    db.commit()
    db.refresh(movimentacao)
    return movimentacao
