from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas.erro import respostas_erro
from app.schemas.usuario import LoginRequest, TokenResponse, UsuarioCreate, UsuarioResponse
from app.security import criar_token, exigir_admin, usuario_atual
from app.services import usuario as service

router = APIRouter(tags=["Autenticação"])


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Faz login e devolve o token JWT",
    responses=respostas_erro(400, 401),
)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = service.autenticar(db, dados.email, dados.senha)
    return TokenResponse(access_token=criar_token(usuario))


@router.get(
    "/auth/me",
    response_model=UsuarioResponse,
    summary="Mostra o usuário dono do token",
    responses=respostas_erro(401),
)
def me(usuario: Usuario = Depends(usuario_atual)):
    return usuario


@router.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um usuário (somente admin)",
    responses=respostas_erro(400, 401, 403, 409),
    dependencies=[Depends(exigir_admin)],
)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    return service.criar(db, dados)
