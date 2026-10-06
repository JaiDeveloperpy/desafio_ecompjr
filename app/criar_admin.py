"""Cria o primeiro administrador pelo terminal.

Necessário porque cadastrar usuário pela API exige um admin logado; sem este
script, o sistema começaria sem ninguém capaz de entrar.

Uso: python -m app.criar_admin "Nome" email@loja.com senha
"""
import sys

from pydantic import ValidationError

from app.database import SessionLocal
from app.exceptions import Conflito
from app.models import Papel
from app.schemas.usuario import UsuarioCreate
from app.services import usuario as service

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit('Uso: python -m app.criar_admin "Nome" email@loja.com senha')
    nome, email, senha = sys.argv[1:]
    try:
        with SessionLocal() as db:
            admin = service.criar(db, UsuarioCreate(nome=nome, email=email, senha=senha, papel=Papel.ADMIN))
    except (Conflito, ValidationError) as erro:
        sys.exit(f"Não foi possível criar o administrador: {erro}")
    print(f"Administrador criado com id {admin.id}.")
