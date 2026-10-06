import threading
from datetime import date, timedelta

from app.exceptions import RegraDeNegocio
from app.models import Produto, TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoCreate
from app.services import movimentacao as movimentacao_service
from tests.conftest import SessaoTeste


def movimentar(client, headers, produto_id, tipo, quantidade):
    return client.post(
        "/movimentacoes",
        json={"produto_id": produto_id, "tipo": tipo, "quantidade": quantidade},
        headers=headers,
    )


def estoque(client, headers, produto_id):
    return client.get(f"/produtos/{produto_id}", headers=headers).json()["quantidade_em_estoque"]


def test_entrada_e_saida_atualizam_estoque(client, admin, produto):
    assert movimentar(client, admin, produto["id"], "entrada", 10).status_code == 201
    assert movimentar(client, admin, produto["id"], "saida", 3).status_code == 201
    assert estoque(client, admin, produto["id"]) == 7


def test_saida_maior_que_estoque_retorna_400_e_nao_registra(client, admin, produto):
    movimentar(client, admin, produto["id"], "entrada", 2)
    resposta = movimentar(client, admin, produto["id"], "saida", 5)
    assert resposta.status_code == 400
    assert "Estoque insuficiente" in resposta.json()["mensagem"]
    assert estoque(client, admin, produto["id"]) == 2
    assert len(client.get("/movimentacoes", headers=admin).json()) == 1


def test_quantidade_zero_retorna_400(client, admin, produto):
    assert movimentar(client, admin, produto["id"], "entrada", 0).status_code == 400


def test_produto_inexistente_retorna_404(client, admin):
    assert movimentar(client, admin, 999, "entrada", 1).status_code == 404


def test_movimentacao_e_imutavel(client, admin, produto):
    movimentacao_id = movimentar(client, admin, produto["id"], "entrada", 1).json()["id"]
    assert client.patch(f"/movimentacoes/{movimentacao_id}", json={"quantidade": 5}, headers=admin).status_code == 405
    assert client.put(f"/movimentacoes/{movimentacao_id}", json={"quantidade": 5}, headers=admin).status_code == 405
    assert client.delete(f"/movimentacoes/{movimentacao_id}", headers=admin).status_code == 405


def test_filtros_por_fornecedor_e_tipo(client, admin, produto):
    movimentar(client, admin, produto["id"], "entrada", 5)
    movimentar(client, admin, produto["id"], "saida", 1)

    do_fornecedor = client.get(f"/movimentacoes?fornecedor_id={produto['fornecedor_id']}", headers=admin)
    assert len(do_fornecedor.json()) == 2
    assert client.get("/movimentacoes?fornecedor_id=999", headers=admin).json() == []
    assert len(client.get("/movimentacoes?tipo=saida", headers=admin).json()) == 1


def test_filtro_por_periodo(client, admin, produto):
    movimentar(client, admin, produto["id"], "entrada", 5)
    hoje = date.today()
    ontem = hoje - timedelta(days=1)

    assert len(client.get(f"/movimentacoes?data_inicio={hoje}&data_fim={hoje}", headers=admin).json()) == 1
    assert client.get(f"/movimentacoes?data_fim={ontem}", headers=admin).json() == []


def test_periodo_invertido_retorna_400(client, admin):
    resposta = client.get("/movimentacoes?data_inicio=2026-10-10&data_fim=2026-10-01", headers=admin)
    assert resposta.status_code == 400


def test_saidas_simultaneas_nao_deixam_estoque_negativo(client, admin, produto):
    movimentar(client, admin, produto["id"], "entrada", 20)

    # 30 vendedores tentam tirar 1 unidade ao mesmo tempo, cada um com sua
    # própria conexão. Sem o lock, várias threads leriam o mesmo estoque e o
    # resultado final ficaria errado. Com o lock, exatamente 20 conseguem.
    largada = threading.Barrier(30)
    resultados = []

    def vender():
        with SessaoTeste() as sessao:
            largada.wait()
            try:
                movimentacao_service.registrar(
                    sessao,
                    MovimentacaoCreate(produto_id=produto["id"], tipo=TipoMovimentacao.SAIDA, quantidade=1),
                )
                resultados.append("ok")
            except RegraDeNegocio:
                resultados.append("sem estoque")

    threads = [threading.Thread(target=vender) for _ in range(30)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert resultados.count("ok") == 20
    assert resultados.count("sem estoque") == 10
    with SessaoTeste() as sessao:
        assert sessao.get(Produto, produto["id"]).quantidade_em_estoque == 0
