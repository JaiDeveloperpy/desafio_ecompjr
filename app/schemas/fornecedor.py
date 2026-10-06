from pydantic import BaseModel, ConfigDict, Field

# CNPJ é guardado só com os 14 dígitos, sem pontuação, para a unicidade
# não ser burlada por formatações diferentes do mesmo número.
CNPJ_REGEX = r"^\d{14}$"
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class FornecedorCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120, examples=["Importadora Oriente"])
    cnpj: str = Field(pattern=CNPJ_REGEX, examples=["12345678000190"])
    telefone: str = Field(min_length=8, max_length=20, examples=["75999990000"])
    email: str = Field(pattern=EMAIL_REGEX, max_length=120, examples=["contato@oriente.com"])

class FornecedorUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    cnpj: str | None = Field(default=None, pattern=CNPJ_REGEX)
    telefone: str | None = Field(default=None, min_length=8, max_length=20)
    email: str | None = Field(default=None, pattern=EMAIL_REGEX, max_length=120)

class FornecedorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cnpj: str
    telefone: str
    email: str
