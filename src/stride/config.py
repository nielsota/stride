import pydantic
import pydantic_settings
from datetime import datetime
from pydantic import Field
from dotenv import load_dotenv


class BaseConfig(pydantic.BaseModel):
    """Base configuration for the application."""

    env_path: str = ".env"


class StravaConfig(pydantic_settings.BaseSettings):
    """Configuration for the Strava connection."""

    client_id: str = Field(alias="STRAVA_CLIENT_ID")
    client_secret: str = Field(alias="STRAVA_CLIENT_SECRET")
    code: str = Field(alias="STRAVA_CODE")
    access_token: str = Field(alias="STRAVA_ACCESS_TOKEN")
    refresh_token: str = Field(alias="STRAVA_REFRESH_TOKEN")
    expires_at: datetime = Field(alias="STRAVA_ACCESS_TOKEN_EXPIRES_AT")

    model_config = pydantic_settings.SettingsConfigDict(env_file=".env")

    def get_bearer_token(self) -> str:
        """Get the bearer token for the Strava API."""
        return f"Bearer {self.access_token}"


def get_strava_config() -> StravaConfig:
    """Get a fresh instance of the Strava config."""
    # Force reload the .env file
    load_dotenv(".env", override=True)
    return StravaConfig()


# For backward compatibility
strava_config = get_strava_config()

if __name__ == "__main__":
    print(get_strava_config())
