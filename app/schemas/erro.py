from pydantic import BaseModel

class ErroCampo(BaseModel):
    campo: str
    erro: str

class ErroResponse(BaseModel):
    status: int
    mensagem: str
    detalhes: list[ErroCampo] | None = None


DESCRICOES_ERRO = {
    400: "Dados inválidos ou regra de negócio violada",
    401: "Token ausente, inválido ou expirado",
    403: "Usuário sem permissão para esta ação",
    404: "Recurso não encontrado",
    409: "Conflito: duplicidade ou vínculo que impede a operação",
}


def respostas_erro(*codigos: int) -> dict:
    """Documenta no Swagger quais erros a rota pode devolver, todos no formato ErroResponse."""
    return {
        codigo: {"model": ErroResponse, "description": DESCRICOES_ERRO[codigo]}
        for codigo in codigos
    }
