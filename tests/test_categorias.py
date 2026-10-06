def test_crud_completo(client, admin):
    criada = client.post("/categorias", json={"nome": "Papelaria"}, headers=admin)
    assert criada.status_code == 201
    categoria_id = criada.json()["id"]

    assert client.get(f"/categorias/{categoria_id}", headers=admin).json()["nome"] == "Papelaria"

    alterada = client.patch(f"/categorias/{categoria_id}", json={"nome": "Escritório"}, headers=admin)
    assert alterada.json()["nome"] == "Escritório"

    assert client.delete(f"/categorias/{categoria_id}", headers=admin).status_code == 204
    assert client.get(f"/categorias/{categoria_id}", headers=admin).status_code == 404


def test_nome_duplicado_retorna_409(client, admin):
    client.post("/categorias", json={"nome": "Papelaria"}, headers=admin)
    resposta = client.post("/categorias", json={"nome": "Papelaria"}, headers=admin)
    assert resposta.status_code == 409


def test_nome_vazio_retorna_400_com_campo(client, admin):
    resposta = client.post("/categorias", json={"nome": ""}, headers=admin)
    assert resposta.status_code == 400
    assert resposta.json()["detalhes"][0]["campo"] == "nome"


def test_inexistente_retorna_404_padronizado(client, admin):
    resposta = client.get("/categorias/999", headers=admin)
    assert resposta.status_code == 404
    assert resposta.json() == {"status": 404, "mensagem": "Categoria 999 não encontrada."}


def test_nao_exclui_categoria_com_produtos(client, admin, produto):
    resposta = client.delete(f"/categorias/{produto['categoria_id']}", headers=admin)
    assert resposta.status_code == 409
    assert client.get(f"/categorias/{produto['categoria_id']}", headers=admin).status_code == 200


def test_erros_de_validacao_e_de_rota_vem_em_portugues(client, admin):
    resposta = client.post("/categorias", json={}, headers=admin)
    assert resposta.json()["detalhes"] == [{"campo": "nome", "erro": "Campo obrigatório."}]

    resposta = client.post("/categorias", json={"nome": ""}, headers=admin)
    assert resposta.json()["detalhes"][0]["erro"] == "Deve ter pelo menos 1 caractere(s)."

    resposta = client.put("/categorias/1", json={"nome": "X"}, headers=admin)
    assert resposta.status_code == 405
    assert resposta.json()["mensagem"] == "Método não permitido para esta rota."
