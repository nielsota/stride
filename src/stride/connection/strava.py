import requests  # type: ignore
from typing import Any

# Replace these with your actual values
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
refresh_token = "YOUR_REFRESH_TOKEN"

url = "https://www.strava.com/oauth/token"

payload = {"client_id": client_id, "client_secret": client_secret, "grant_type": "refresh_token", "refresh_token": refresh_token}

response = requests.post(url, data=payload)


def get_strava_access_token(client_id: str, client_secret: str, code: str) -> dict:
    """
    Exchange an authorization code for a Strava access token.
    """
    url = "https://www.strava.com/oauth/token"
    payload = {"client_id": client_id, "client_secret": client_secret, "code": code, "grant_type": "authorization_code"}
    response = requests.post(url, data=payload)
    response.raise_for_status()  # Raises an error for bad responses
    return response.json()


def refresh_strava_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    """
    Use a refresh token to obtain a new Strava access token.
    """
    url = "https://www.strava.com/oauth/token"
    payload = {"client_id": client_id, "client_secret": client_secret, "grant_type": "refresh_token", "refresh_token": refresh_token}
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()


def list_strava_activities(access_token: str, per_page: int = 30, page: int = 1) -> list[dict[str, Any]]:
    """
    List activities for the authenticated Strava athlete.

    Args:
        access_token: The Bearer token (access token) for authentication.
        per_page: Number of activities per page (default 30, max 200).
        page: Page number to retrieve (default 1).

    Returns:
        A list of activity dictionaries.
    """
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": per_page, "page": page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
