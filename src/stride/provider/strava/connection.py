import requests  # type: ignore
from dotenv import load_dotenv, set_key
from datetime import datetime, timezone
from loguru import logger

from stride.config import get_strava_config
from .endpoints import StravaEndpoints
from .models import StravaAccessTokenResponse

# Load environment variables from .env file
strava_config = get_strava_config()


def _refresh_strava_access_token() -> StravaAccessTokenResponse:
    """Use a refresh token to obtain a new Strava access token."""
    url = StravaEndpoints.TOKEN.value
    payload = {
        "client_id": strava_config.client_id,
        "client_secret": strava_config.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": strava_config.refresh_token,
    }
    logger.debug("Refreshing Strava access token.")
    response = requests.post(url, data=payload)
    response.raise_for_status()
    logger.debug("Refreshed Strava access token.")
    return StravaAccessTokenResponse(**response.json())


def _update_strava_access_token(env_path: str = ".env") -> bool:
    """Update the Strava access token and refresh token in the .env file."""
    response = _refresh_strava_access_token()
    load_dotenv(env_path, override=True)
    logger.debug(f"Updating env variables in {env_path}")
    set_key(env_path, "STRAVA_ACCESS_TOKEN", response.access_token)
    set_key(env_path, "STRAVA_REFRESH_TOKEN", response.refresh_token)
    set_key(env_path, "STRAVA_ACCESS_TOKEN_EXPIRES_AT", str(response.expires_at))
    logger.debug(f"Updated env variables in {env_path}")
    return True


def _check_strava_access_token_validity() -> bool:
    """Check if the Strava access token is valid."""
    return strava_config.expires_at > datetime.now(timezone.utc)


def update_strava_config(env_path: str = ".env") -> bool:
    """Update the Strava config in the .env file."""
    if _check_strava_access_token_validity():
        logger.info("Strava access token is valid, skipping update")
        return True
    logger.info("Strava access token is invalid, updating...")
    return _update_strava_access_token(env_path)
