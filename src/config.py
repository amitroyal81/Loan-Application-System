"""Application configuration management"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Anthropic API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # LLM
    llm_model: str = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    # MCP Servers
    applicant_db_host: str = os.getenv("APPLICANT_DB_HOST", "localhost")
    applicant_db_port: int = int(os.getenv("APPLICANT_DB_PORT", "8001"))

    risk_rules_db_host: str = os.getenv("RISK_RULES_DB_HOST", "localhost")
    risk_rules_db_port: int = int(os.getenv("RISK_RULES_DB_PORT", "8002"))

    decision_synthesis_host: str = os.getenv("DECISION_SYNTHESIS_HOST", "localhost")
    decision_synthesis_port: int = int(os.getenv("DECISION_SYNTHESIS_PORT", "8003"))

    notification_system_host: str = os.getenv("NOTIFICATION_SYSTEM_HOST", "localhost")
    notification_system_port: int = int(os.getenv("NOTIFICATION_SYSTEM_PORT", "8004"))

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
