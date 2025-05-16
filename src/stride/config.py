import pydantic
from datetime import datetime
import os
from pydantic import Field
from dotenv import load_dotenv


class BaseConfig(pydantic.BaseModel):
    """Base configuration for the application."""

    env_path: str = ".env"


class StravaConfig(BaseConfig):
    """Configuration for the Strava connection."""

    client_id: str = Field(alias="STRAVA_CLIENT_ID")
    client_secret: str = Field(alias="STRAVA_CLIENT_SECRET")
    code: str = Field(alias="STRAVA_CODE")
    access_token: str = Field(alias="STRAVA_ACCESS_TOKEN")
    refresh_token: str = Field(alias="STRAVA_REFRESH_TOKEN")
    expires_at: datetime = Field(alias="STRAVA_ACCESS_TOKEN_EXPIRES_AT")
    
    # TODO: use model config to set env_file to .env

    @classmethod
    def from_env(cls) -> "StravaConfig":
        """Load the configuration from the environment variables."""
        # Force reload by finding the .env file and loading it with override
        load_dotenv(override=True)

        fields_aliases = [field.alias for field in cls.model_fields.values()]
        env_vars = {k: v for k, v in os.environ.items() if k in fields_aliases}
        return cls(**env_vars)

    def get_bearer_token(self) -> str:
        """Get the bearer token for the Strava API."""
        return f"Bearer {self.access_token}"


strava_config = StravaConfig.from_env()

if __name__ == "__main__":
    print(strava_config)
