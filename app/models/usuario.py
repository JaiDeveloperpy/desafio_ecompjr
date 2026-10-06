import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Papel(str, enum.Enum):
    # admin gerencia o catálogo; funcionario consulta e registra movimentações.
    ADMIN = "admin"
    FUNCIONARIO = "funcionario"

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    # Nunca a senha em texto puro, só o hash com salt (ver app/security.py).
    senha_hash: Mapped[str] = mapped_column(String(255))
    papel: Mapped[Papel] = mapped_column(Enum(Papel, name="papel_usuario"))
