from pydantic import BaseModel

class ErroCampo(BaseModel):
    campo: str
    erro: str

class ErroResponse(BaseModel):
    status: int
    mensagem: str
    detalhes: list[ErroCampo] | None = None


def respostas_erro(*codigos: int) -> dict:
    """Documenta no Swagger quais erros a rota pode devolver, todos no formato ErroResponse."""
    return {codigo: {"model": ErroResponse} for codigo in codigos}
