from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import Conflito, NaoAutenticado
from app.models import Usuario
from app.schemas.usuario import UsuarioCreate
from app.security import gerar_hash, verificar_senha


def criar(db: Session, dados: UsuarioCreate) -> Usuario:
    if db.scalar(select(Usuario).where(Usuario.email == dados.email)):
        raise Conflito("Já existe um usuário com este email.")
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash(dados.senha),
        papel=dados.papel,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    # Mesma mensagem para email inexistente e senha errada: assim a API não
    # revela quais emails estão cadastrados.
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutenticado("Email ou senha incorretos.")
    return usuario
