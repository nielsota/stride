import requests
from loguru import logger
from typing import Any
from stride.config import get_strava_config

strava_config = get_strava_config()


def _strava_request(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    """Make a request to the Strava API."""
    params = params or {}
    logger.debug(f"Making request to {url} with params {params}")
    headers = {"Authorization": strava_config.get_bearer_token()}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response
