from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.errors import registrar_handlers
from app.routers import auth, categoria, fornecedor, movimentacao, produto

app = FastAPI(
    title="API de Estoque",
    description=(
        "Estoque da loja: categorias, fornecedores, produtos e movimentações.\n\n"
        "Para usar: faça login em POST /auth/login, copie o access_token e clique em "
        "Authorize. Administradores gerenciam o catálogo; funcionários consultam e "
        "registram movimentações."
    ),
    version="1.0.0",
)
registrar_handlers(app)

app.include_router(auth.router)
app.include_router(categoria.router)
app.include_router(fornecedor.router)
app.include_router(produto.router)
app.include_router(movimentacao.router)


@app.get("/health", tags=["Saúde"], summary="Verifica se a API está no ar")
def health():
    return {"status": "ok"}


def openapi_em_portugues():
    # O FastAPI documenta sozinho uma resposta 422 em toda rota, mas esta API
    # devolve 400 nos erros de validação (ver errors.py). Removemos o 422 para
    # o Swagger não prometer algo que não acontece, e traduzimos o texto
    # padrão de sucesso, que vem em inglês.
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title, version=app.version, description=app.description, routes=app.routes
    )
    for operacoes in schema["paths"].values():
        for operacao in operacoes.values():
            respostas = operacao["responses"]
            respostas.pop("422", None)
            for resposta in respostas.values():
                if resposta.get("description") == "Successful Response":
                    resposta["description"] = "Sucesso"
    for nome in ("HTTPValidationError", "ValidationError"):
        schema.get("components", {}).get("schemas", {}).pop(nome, None)
    app.openapi_schema = schema
    return schema


app.openapi = openapi_em_portugues
