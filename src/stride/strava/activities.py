import enum
import pydantic
from datetime import datetime
from typing import Optional

from stride.config import strava_config
from stride.connections.strava import StravaEndpoint

import requests  # type: ignore


class StravaActivity(pydantic.BaseModel):
    """Model representing a Strava activity."""

    id: int
    name: str
    distance: float  # in meters
    moving_time: int  # in seconds
    elapsed_time: int  # in seconds
    total_elevation_gain: float  # in meters
    type: str  # e.g., "Run", "Ride", "Swim"
    start_date: datetime
    start_date_local: datetime
    timezone: str
    average_speed: float  # in meters per second
    max_speed: float  # in meters per second
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    elev_high: Optional[float] = None  # in meters
    elev_low: Optional[float] = None  # in meters
    description: Optional[str] = None
    calories: Optional[float] = None
    has_heartrate: bool = False
    average_cadence: Optional[float] = None
    average_watts: Optional[float] = None
    max_watts: Optional[float] = None
    weighted_average_watts: Optional[float] = None
    kilojoules: Optional[float] = None
    device_watts: Optional[bool] = None
    average_temp: Optional[float] = None
    suffer_score: Optional[int] = None


class StreamType(str, enum.Enum):
    TIME = "time"
    DISTANCE = "distance"
    LATLNG = "latlng"
    ALTITUDE = "altitude"
    VELOCITY_SMOOTH = "velocity_smooth"
    HEARTRATE = "heartrate"
    CADENCE = "cadence"
    WATTS = "watts"
    TEMP = "temp"
    MOVING = "moving"
    GRADE_SMOOTH = "grade_smooth"


class Stream(pydantic.BaseModel):
    """Model representing a Strava stream."""

    type: StreamType
    data: list[float]


def list_strava_activities(per_page: int = 2, page: int = 1) -> list[StravaActivity]:
    """List activities for the authenticated Strava athlete."""
    # Reload config each time to get fresh values

    url = StravaEndpoint.ATHLETE_ACTIVITIES.value
    headers = {"Authorization": strava_config.get_bearer_token()}
    params = {"per_page": per_page, "page": page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # Convert the JSON response to StravaActivity objects
    activities_data = response.json()
    return [StravaActivity(**activity) for activity in activities_data]


def get_strava_activity(activity_id: int) -> StravaActivity:
    """Get a specific Strava activity by ID."""
    # Remove the /athlete prefix from the base URL
    base_url = StravaEndpoint.ACTIVITY.value
    url = base_url.format(activity_id=activity_id)
    headers = {"Authorization": strava_config.get_bearer_token()}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(response.json())
    return StravaActivity(**response.json())


def get_strava_activity_streams(activity_id: int) -> list[Stream]:
    """Get streams for a specific Strava activity by ID."""
    # Remove the /athlete prefix from the base URL
    base_url = StravaEndpoint.ACTIVITY_STREAMS.value
    url = base_url.format(activity_id=activity_id)
    headers = {"Authorization": strava_config.get_bearer_token()}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return [Stream(**stream) for stream in response.json()]


def get_strava_activity_stream_by_type(activity_id: int, stream_type: StreamType) -> Stream:
    """Get a specific stream for a Strava activity by type."""
    base_url = StravaEndpoint.ACTIVITY_STREAMS_BY_TYPE.value
    url = base_url.format(activity_id=activity_id, stream_type=stream_type)
    print(url)
    headers = {"Authorization": strava_config.get_bearer_token()}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # print(response.json())
    return Stream(**response.json())


if __name__ == "__main__":
    # Test the list_strava_activities function
    activities = list_strava_activities()
    # print(activities)

    # Test the get_strava_activity function
    test_id = activities[0].id
    print(get_strava_activity(test_id))

    # Test the get_strava_activity_streams function
    # print(get_strava_activity_streams(test_id))

    # Test the get_strava_activity_stream_by_type function
    print(get_strava_activity_stream_by_type(test_id, StreamType.HEARTRATE))
