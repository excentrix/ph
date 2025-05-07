from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_PREFIX: str = "/api"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: Union[int, str] = 5432
    
    # Database URL
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Neo4j
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: Union[int, str] = 6379
    
    # LLM
    LLM_MODEL: str = "gpt-3.5-turbo"
    OPENAI_API_KEY: str
    
    # Vector DB
    VECTOR_DB_DIR: str = "./data/vector_db"
    
    # Model config
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Create settings instance
settings = Settings()
