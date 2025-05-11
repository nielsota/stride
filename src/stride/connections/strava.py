import requests  # type: ignore
import pydantic
import enum
from dotenv import load_dotenv, set_key
from datetime import datetime, timezone
from loguru import logger

from stride.config import strava_config

# Load environment variables from .env file
load_dotenv()


class StravaEndpoint(str, enum.Enum):
    TOKEN = "https://www.strava.com/oauth/token"
    ATHLETE_ACTIVITIES = "https://www.strava.com/api/v3/athlete/activities"
    ACTIVITY = "https://www.strava.com/api/v3/activities/{activity_id}"
    ACTIVITY_STREAMS = "https://www.strava.com/api/v3/activities/{activity_id}/streams"
    ACTIVITY_STREAMS_BY_TYPE = "https://www.strava.com/api/v3/activities/{activity_id}/streams/{stream_type}"


class StravaAccessTokenResponse(pydantic.BaseModel):
    """Response from the Strava API when refreshing an access token."""

    token_type: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    expires_in: int


def refresh_strava_access_token() -> StravaAccessTokenResponse:
    """Use a refresh token to obtain a new Strava access token."""
    url = StravaEndpoint.TOKEN.value
    payload = {"client_id": strava_config.client_id, "client_secret": strava_config.client_secret, "grant_type": "refresh_token", "refresh_token": strava_config.refresh_token}
    logger.debug("Refreshing Strava access token.")
    response = requests.post(url, data=payload)
    response.raise_for_status()
    logger.debug("Refreshed Strava access token.")
    return StravaAccessTokenResponse(**response.json())


def update_strava_access_token(env_path: str = ".env") -> bool:
    """Update the Strava access token and refresh token in the .env file."""
    response = refresh_strava_access_token()
    load_dotenv(env_path, override=True)
    logger.debug(f"Updating env variables in {env_path}")
    set_key(env_path, "STRAVA_ACCESS_TOKEN", response.access_token)
    set_key(env_path, "STRAVA_REFRESH_TOKEN", response.refresh_token)
    set_key(env_path, "STRAVA_ACCESS_TOKEN_EXPIRES_AT", str(response.expires_at))
    logger.debug(f"Updated env variables in {env_path}")
    return True


def check_strava_access_token_validity() -> bool:
    """Check if the Strava access token is valid."""
    return strava_config.expires_at > datetime.now(timezone.utc)


def update_strava_config(env_path: str = ".env") -> bool:
    """Update the Strava config in the .env file."""
    if check_strava_access_token_validity():
        logger.info("Strava access token is valid, skipping update")
        return True
    logger.info("Strava access token is invalid, updating...")
    return update_strava_access_token(env_path)


if __name__ == "__main__":
    # print(list_strava_activities(access_token))
    # print(refresh_strava_access_token(client_id, client_secret, refresh_token))
    # print(update_strava_access_token())
    # print(check_strava_access_token_validity())
    print(update_strava_config())
