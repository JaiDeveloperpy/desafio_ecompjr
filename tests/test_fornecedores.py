FORNECEDOR = {
    "nome": "Casa do Chá",
    "cnpj": "11222333000144",
    "telefone": "75988887777",
    "email": "vendas@casadocha.com",
}


def test_crud_completo(client, admin):
    criado = client.post("/fornecedores", json=FORNECEDOR, headers=admin)
    assert criado.status_code == 201
    fornecedor_id = criado.json()["id"]

    alterado = client.patch(f"/fornecedores/{fornecedor_id}", json={"telefone": "75911112222"}, headers=admin)
    assert alterado.json()["telefone"] == "75911112222"
    assert alterado.json()["cnpj"] == FORNECEDOR["cnpj"]

    assert client.delete(f"/fornecedores/{fornecedor_id}", headers=admin).status_code == 204


def test_cnpj_duplicado_retorna_409(client, admin):
    client.post("/fornecedores", json=FORNECEDOR, headers=admin)
    resposta = client.post("/fornecedores", json={**FORNECEDOR, "email": "outro@email.com"}, headers=admin)
    assert resposta.status_code == 409


def test_email_duplicado_retorna_409(client, admin):
    client.post("/fornecedores", json=FORNECEDOR, headers=admin)
    resposta = client.post("/fornecedores", json={**FORNECEDOR, "cnpj": "99888777000166"}, headers=admin)
    assert resposta.status_code == 409


def test_cnpj_com_pontuacao_retorna_400(client, admin):
    resposta = client.post("/fornecedores", json={**FORNECEDOR, "cnpj": "11.222.333/0001-44"}, headers=admin)
    assert resposta.status_code == 400


def test_nao_exclui_fornecedor_com_produtos(client, admin, produto):
    resposta = client.delete(f"/fornecedores/{produto['fornecedor_id']}", headers=admin)
    assert resposta.status_code == 409
