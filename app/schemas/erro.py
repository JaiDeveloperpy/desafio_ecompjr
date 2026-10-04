from pydantic import BaseModel

class ErroCampo(BaseModel):
    campo: str
    erro: str

class ErroResponse(BaseModel):
    status: int
    mensagem: str
    detalhes: list[ErroCampo] | None = None