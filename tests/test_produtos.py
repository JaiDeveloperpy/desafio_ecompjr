def test_produto_nasce_com_estoque_zero(produto):
    assert produto["quantidade_em_estoque"] == 0
    assert produto["preco_venda"] == "29.90"


def test_categoria_inexistente_retorna_404(client, admin, produto):
    dados = {
        "nome": "Vaso",
        "sku": "VAS-001",
        "preco_custo": "5.00",
        "preco_venda": "10.00",
        "categoria_id": 999,
        "fornecedor_id": produto["fornecedor_id"],
    }
    assert client.post("/produtos", json=dados, headers=admin).status_code == 404


def test_sku_duplicado_retorna_409(client, admin, produto):
    dados = {
        "nome": "Outra luminária",
        "sku": produto["sku"],
        "preco_custo": "1.00",
        "preco_venda": "2.00",
        "categoria_id": produto["categoria_id"],
        "fornecedor_id": produto["fornecedor_id"],
    }
    assert client.post("/produtos", json=dados, headers=admin).status_code == 409


def test_patch_nao_altera_estoque(client, admin, produto):
    resposta = client.patch(
        f"/produtos/{produto['id']}",
        json={"nome": "Luminária grande", "quantidade_em_estoque": 999},
        headers=admin,
    )
    assert resposta.json()["nome"] == "Luminária grande"
    assert resposta.json()["quantidade_em_estoque"] == 0


def test_estoque_baixo(client, admin, produto):
    # Estoque 0 com mínimo 5: aparece na lista.
    ids = [p["id"] for p in client.get("/produtos/estoque-baixo", headers=admin).json()]
    assert produto["id"] in ids

    # Exatamente no mínimo ainda conta como estoque baixo.
    client.post("/movimentacoes", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 5}, headers=admin)
    assert len(client.get("/produtos/estoque-baixo", headers=admin).json()) == 1

    # Acima do mínimo sai da lista.
    client.post("/movimentacoes", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1}, headers=admin)
    assert client.get("/produtos/estoque-baixo", headers=admin).json() == []


def test_filtro_por_nome(client, admin, produto):
    assert len(client.get("/produtos?nome=lumin", headers=admin).json()) == 1
    assert client.get("/produtos?nome=cadeira", headers=admin).json() == []


def test_nao_exclui_produto_com_movimentacoes(client, admin, produto):
    client.post("/movimentacoes", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1}, headers=admin)
    assert client.delete(f"/produtos/{produto['id']}", headers=admin).status_code == 409


def test_exclui_produto_sem_movimentacoes(client, admin, produto):
    assert client.delete(f"/produtos/{produto['id']}", headers=admin).status_code == 204
