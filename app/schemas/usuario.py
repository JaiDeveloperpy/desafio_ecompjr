from pydantic import BaseModel, ConfigDict, Field

from app.models.usuario import Papel

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class LoginRequest(BaseModel):
    email: str = Field(examples=["admin@loja.com"])
    senha: str = Field(examples=["senha-forte-123"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120, examples=["Maria Souza"])
    email: str = Field(pattern=EMAIL_REGEX, max_length=120, examples=["maria@loja.com"])
    senha: str = Field(min_length=8, examples=["senha-forte-123"])
    papel: Papel = Papel.FUNCIONARIO

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    papel: Papel
