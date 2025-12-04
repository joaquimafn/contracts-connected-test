import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env file - look in multiple locations
def find_env_file():
    """Find .env file in parent directories."""
    current = Path(__file__).parent.parent.parent  # backend folder

    # Check: backend/.env, project_root/.env
    for potential_path in [
        current / "backend" / ".env",  # backend dir (priority)
        current / ".env",  # project root
    ]:
        if potential_path.exists():
            print(f"[CONFIG] Found .env at: {potential_path}")
            return str(potential_path)

    print(f"[CONFIG WARNING] No .env file found. Checked: {current}/backend/.env, {current}/.env")
    return str(current / "backend" / ".env")


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY", description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")

    # Application Settings
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    allowed_file_types: str = Field(default="pdf,txt", env="ALLOWED_FILE_TYPES")

    # CORS Settings
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        env="CORS_ORIGINS"
    )

    # Analysis Settings
    max_concurrent_analyses: int = Field(default=5, env="MAX_CONCURRENT_ANALYSES")
    analysis_timeout_seconds: int = Field(default=300, env="ANALYSIS_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

    def get_allowed_file_types(self) -> list:
        """Get list of allowed file types."""
        return [ft.strip() for ft in self.allowed_file_types.split(",")]

    def get_cors_origins(self) -> list:
        """Get list of CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def validate_openai_key(self) -> None:
        """Validate that OpenAI API key is configured."""
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Please set OPENAI_API_KEY environment variable or add it to .env file"
            )


try:
    settings = Settings()
    # Validate API key exists
    settings.validate_openai_key()
    print("[CONFIG] Settings loaded successfully")
    print(f"[CONFIG] - Environment: {settings.environment}")
    print(f"[CONFIG] - Model: {settings.openai_model}")
    print(f"[CONFIG] - API Key: {'*' * 20}...{settings.openai_api_key[-4:] if settings.openai_api_key else 'NOT SET'}")
except ValueError as e:
    import sys
    print(f"[CONFIG ERROR] {str(e)}", file=sys.stderr)
    raise
