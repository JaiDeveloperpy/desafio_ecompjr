import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import (
    Conflito,
    NaoAutenticado,
    NaoEncontrado,
    RegraDeNegocio,
    SemPermissao,
)

logger = logging.getLogger("app")

def resposta_erro(
    status: int, mensagem: str, detalhes: list | None = None
) -> JSONResponse:
    corpo = {"status": status, "mensagem": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    return JSONResponse(status_code=status, content=corpo)


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(NaoEncontrado)
    async def nao_encontrado(request: Request, exc: NaoEncontrado):
        return resposta_erro(404, str(exc))

    @app.exception_handler(Conflito)
    async def conflito(request: Request, exc: Conflito):
        return resposta_erro(409, str(exc))

    @app.exception_handler(RegraDeNegocio)
    async def regra_de_negocio(request: Request, exc: RegraDeNegocio):
        return resposta_erro(400, str(exc))

    @app.exception_handler(NaoAutenticado)
    async def nao_autenticado(request: Request, exc: NaoAutenticado):
        return resposta_erro(401, str(exc))

    @app.exception_handler(SemPermissao)
    async def sem_permissao(request: Request, exc: SemPermissao):
        return resposta_erro(403, str(exc))

    @app.exception_handler(RequestValidationError)
    async def dados_invalidos(request: Request, exc: RequestValidationError):
        detalhes = [
            {"campo": ".".join(str(p) for p in erro["loc"][1:]), "erro": erro["msg"]}
            for erro in exc.errors()
        ]
        return resposta_erro(400, "Dados inválidos.", detalhes)

    @app.exception_handler(IntegrityError)
    async def violacao_no_banco(request: Request, exc: IntegrityError):
        # Rede de segurança: o service confere antes, mas duas requisições
        # simultâneas podem passar pela conferência e só o banco barra.
        return resposta_erro(409, "A operação viola uma restrição do banco de dados.")

    @app.exception_handler(StarletteHTTPException)
    async def erro_http(request: Request, exc: StarletteHTTPException):
        return resposta_erro(exc.status_code, str(exc.detail))

    @app.exception_handler(Exception)
    async def erro_interno(request: Request, exc: Exception):
        logger.exception("Erro não tratado em %s %s", request.method, request.url.path)
        return resposta_erro(500, "Erro interno do servidor.")
