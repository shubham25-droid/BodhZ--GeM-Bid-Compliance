import os
from pydantic_settings import BaseSettings, SettingsConfigDict


# --------------------------------------------------
# APPLICATION CONFIGURATION CLASS
# --------------------------------------------------
class Settings(BaseSettings):
    """
    Centralized configuration management for the BodhZ backend application.
    Reads environment variables with fallback defaults.
    """
    PROJECT_NAME: str = "BodhZ — GeM Bid Compliance Platform"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # Security Configuration
    SECRET_KEY: str = "bodhz_sih26100_super_secret_jwt_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./bodhz_dev.db"
    
    # File Storage Configuration
    UPLOAD_DIR: str = "D:/Antigravity Workspace/BodhZ_Bid Compliance Project (SIH26100)/backend/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    
    # Rate Limiting & CORS
    RATE_LIMIT_DEFAULT: str = "10/second"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # OpenAI API Configuration (Backend Only)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
