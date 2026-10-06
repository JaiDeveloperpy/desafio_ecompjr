from fastapi import FastAPI
from app.errors import registrar_handlers
from app.routers import categoria, fornecedor, produto

app = FastAPI(
    title="API de Estoque",
    description="Estoque da loja: categorias, fornecedores, produtos e movimentações.",
    version="1.0.0",
)
registrar_handlers(app)

app.include_router(categoria.router)
app.include_router(fornecedor.router)
app.include_router(produto.router)


@app.get("/health", tags=["Saúde"])
def health():
    return {"status": "ok"}
