from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    # App
    app_name: str = "BotChatWhatsAppPizzaria"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=5000, alias="PORT")
    
    # WhatsApp Business API
    whatsapp_verify_token: str = Field(default="", alias="WHATSAPP_VERIFY_TOKEN")
    whatsapp_phone_number_id: str = Field(default="", alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_access_token: str = Field(default="", alias="WHATSAPP_ACCESS_TOKEN")
    whatsapp_app_secret: str = Field(default="", alias="WHATSAPP_APP_SECRET")
    
    # Google Gemini AI
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-pro", alias="GEMINI_MODEL")
    
    # SQLite
    sqlite_db_path: str = Field(default="pizzaria.db", alias="SQLITE_DB_PATH")
    
    # Google Sheets
    google_credentials_path: str = Field(default="credentials.json", alias="GOOGLE_CREDENTIALS_PATH")
    google_sheets_name: str = Field(default="Pedidos da Pizzaria", alias="GOOGLE_SHEETS_NAME")
    
    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", alias="CELERY_RESULT_BACKEND")
    
    # WhatsApp Business number (for customer wa.me links)
    empresa_numero: str = Field(default="5511999999999", alias="EMPRESA_NUMERO")
    
    # PIX
    pix_key: str = Field(default="111.222.333-44 (CPF)", alias="PIX_KEY")
    
    # Session
    session_ttl_seconds: int = Field(default=1800, alias="SESSION_TTL_SECONDS")  # 30 min
    session_prefix: str = Field(default="pizzaria:session:", alias="SESSION_PREFIX")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # Store hours (HH:MM format)
    loja_abertura: str = Field(default="18:00", alias="LOJA_ABERTURA")
    loja_fechamento: str = Field(default="00:00", alias="LOJA_FECHAMENTO")
    loja_dias: str = Field(default="0,1,2,3,4,5,6", alias="LOJA_DIAS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @property
    def redis_connection_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"
    
    def is_loja_aberta(self) -> bool:
        return True


settings = Settings()