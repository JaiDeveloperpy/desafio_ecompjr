def test_login_devolve_token_que_da_acesso(client, admin):
    resposta = client.post("/auth/login", json={"email": "admin@loja.com", "senha": "senha-de-teste"})
    assert resposta.status_code == 200
    token = resposta.json()["access_token"]
    eu = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert eu.json()["papel"] == "admin"


def test_senha_errada_retorna_401(client, admin):
    resposta = client.post("/auth/login", json={"email": "admin@loja.com", "senha": "errada"})
    assert resposta.status_code == 401
    assert resposta.json()["mensagem"] == "Email ou senha incorretos."


def test_sem_token_retorna_401(client):
    assert client.get("/produtos").status_code == 401


def test_token_invalido_retorna_401(client):
    assert client.get("/produtos", headers={"Authorization": "Bearer abc.def.ghi"}).status_code == 401


def test_funcionario_consulta_e_movimenta_mas_nao_altera_catalogo(client, funcionario, produto):
    assert client.get("/produtos", headers=funcionario).status_code == 200
    movimento = client.post(
        "/movimentacoes",
        json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 1},
        headers=funcionario,
    )
    assert movimento.status_code == 201

    assert client.post("/categorias", json={"nome": "Nova"}, headers=funcionario).status_code == 403
    assert client.patch(f"/produtos/{produto['id']}", json={"nome": "X"}, headers=funcionario).status_code == 403
    assert client.delete(f"/produtos/{produto['id']}", headers=funcionario).status_code == 403


def test_somente_admin_cadastra_usuarios(client, admin, funcionario):
    novo = {"nome": "Ana", "email": "ana@loja.com", "senha": "senha-forte-123"}
    assert client.post("/usuarios", json=novo, headers=funcionario).status_code == 403

    criado = client.post("/usuarios", json=novo, headers=admin)
    assert criado.status_code == 201
    assert criado.json()["papel"] == "funcionario"
    assert "senha" not in criado.json()
    assert "senha_hash" not in criado.json()
