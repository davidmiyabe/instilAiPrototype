"""
Configuration management for the nonprofit CRM application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API Configuration
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Database Configuration
    database_url: str = "sqlite:///nonprofit_crm.db"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"

    # Message Generator Configuration
    default_message_length: int = 220
    min_message_length: int = 150
    max_message_length: int = 500
    default_tone: str = "warm, human, relationship-forward"
    generate_alternates: bool = False
    num_alternates: int = 3

    # Application Configuration
    app_name: str = "Nonprofit CRM"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
