from fastapi import FastAPI
from app.errors import registrar_handlers
app = FastAPI(
    title="API de Estoque",
    description="Estoque da loja: categorias, fornecedores, produtos e movimentações.",
    version="1.0.0",

)
registrar_handlers(app)


@app.get("/health", tags=["Saúde"])
def health():
    return {"status": "ok"}