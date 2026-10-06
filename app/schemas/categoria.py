from pydantic import BaseModel, ConfigDict, Field

class CategoriaCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=80, examples=["Eletrônicos"])

class CategoriaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=80)

class CategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
