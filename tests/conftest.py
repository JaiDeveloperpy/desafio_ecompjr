import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Papel
from app.schemas.usuario import UsuarioCreate
from app.security import criar_token
from app.services import usuario as usuario_service

# Banco separado do de desenvolvimento: os testes apagam todas as tabelas
# entre um caso e outro, então nunca podem apontar para dados reais.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", settings.database_url + "_teste")

engine = create_engine(TEST_DATABASE_URL)
SessaoTeste = sessionmaker(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def limpar_tabelas():
    # Cada teste começa com o banco vazio, então a ordem de execução não importa.
    yield
    tabelas = ", ".join(tabela.name for tabela in Base.metadata.sorted_tables)
    with engine.begin() as conexao:
        conexao.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))


@pytest.fixture
def db():
    with SessaoTeste() as sessao:
        yield sessao


@pytest.fixture
def client():
    def get_db_teste():
        with SessaoTeste() as sessao:
            yield sessao

    app.dependency_overrides[get_db] = get_db_teste
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


def _cabecalho_de(db, papel: Papel) -> dict:
    usuario = usuario_service.criar(
        db,
        UsuarioCreate(
            nome=papel.value,
            email=f"{papel.value}@loja.com",
            senha="senha-de-teste",
            papel=papel,
        ),
    )
    return {"Authorization": f"Bearer {criar_token(usuario)}"}


@pytest.fixture
def admin(db):
    return _cabecalho_de(db, Papel.ADMIN)


@pytest.fixture
def funcionario(db):
    return _cabecalho_de(db, Papel.FUNCIONARIO)


@pytest.fixture
def produto(client, admin):
    """Produto pronto para uso, com categoria e fornecedor já criados."""
    categoria = client.post("/categorias", json={"nome": "Decoração"}, headers=admin).json()
    fornecedor = client.post(
        "/fornecedores",
        json={
            "nome": "Importadora Oriente",
            "cnpj": "12345678000190",
            "telefone": "75999990000",
            "email": "contato@oriente.com",
        },
        headers=admin,
    ).json()
    return client.post(
        "/produtos",
        json={
            "nome": "Luminária de papel",
            "sku": "LUM-001",
            "preco_custo": "12.50",
            "preco_venda": "29.90",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
        headers=admin,
    ).json()
