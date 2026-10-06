from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    # Sem valor padrão de propósito: se a chave não estiver configurada, a API
    # nem sobe, em vez de rodar assinando tokens com um segredo conhecido.
    jwt_secret: str
    jwt_expira_minutos: int = 60


settings = Settings()
