from fastapi import FastAPI
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


@app.get("/health", tags=["Saúde"])
def health():
    return {"status": "ok"}

