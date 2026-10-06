import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.exceptions import NaoAutenticado, SemPermissao
from app.models import Papel, Usuario

ALGORITMO = "HS256"

# auto_error=False: sem token, quem responde é o nosso handler (401 no formato
# padrão da API), e não a mensagem própria do FastAPI.
bearer = HTTPBearer(auto_error=False)


# scrypt da biblioteca padrão: é lento de propósito e usa salt aleatório por
# usuário, o que torna inviável quebrar as senhas por força bruta ou tabela pronta.
def gerar_hash(senha: str) -> str:
    salt = secrets.token_bytes(16)
    hash_ = hashlib.scrypt(senha.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}${hash_.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    salt_hex, hash_hex = senha_hash.split("$")
    hash_ = hashlib.scrypt(senha.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
    # compare_digest leva o mesmo tempo acertando ou errando, então não dá
    # para descobrir o hash medindo quanto a resposta demora.
    return hmac.compare_digest(hash_.hex(), hash_hex)


def criar_token(usuario: Usuario) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expira_minutos)
    dados = {"sub": str(usuario.id), "papel": usuario.papel.value, "exp": expira}
    return jwt.encode(dados, settings.jwt_secret, algorithm=ALGORITMO)


def usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciais is None:
        raise NaoAutenticado("Token de acesso não informado.")
    try:
        dados = jwt.decode(credenciais.credentials, settings.jwt_secret, algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise NaoAutenticado("Token expirado, faça login novamente.")
    except jwt.InvalidTokenError:
        raise NaoAutenticado("Token inválido.")
    # Busca no banco em vez de confiar só no token: se o usuário for removido,
    # o token dele para de valer na hora.
    usuario = db.get(Usuario, int(dados["sub"]))
    if usuario is None:
        raise NaoAutenticado("Usuário do token não existe mais.")
    return usuario


def exigir_admin(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    if usuario.papel != Papel.ADMIN:
        raise SemPermissao("Apenas administradores podem realizar esta ação.")
    return usuario
