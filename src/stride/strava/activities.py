from stride.config import strava_config
from stride.connections.strava import StravaEndpoint

import requests  # type: ignore
from typing import Any


def list_strava_activities(per_page: int = 30, page: int = 1) -> list[dict[str, Any]]:
    """List activities for the authenticated Strava athlete."""
    url = StravaEndpoint.ACTIVITIES.value
    headers = {"Authorization": f"Bearer {strava_config.access_token}"}
    params = {"per_page": per_page, "page": page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()  # type: ignore[no-any-return]
