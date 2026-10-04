from fastapi import FastAPI

app = FastAPI(
    title="API de Estoque",
    description="Estoque da loja: categorias, fornecedores, produtos e movimentações.",
    version="1.0.0",

)


@app.get("/health", tags=["Saúde"])
def health():
    return {"status": "ok"}