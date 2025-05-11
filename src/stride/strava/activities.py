import enum
import pydantic
from datetime import datetime
from typing import Optional, Any

from stride.config import strava_config
from stride.connections.strava import StravaEndpoint

import requests  # type: ignore


class StreamType(str, enum.Enum):
    """Types of data streams available from Strava."""

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


class Stream(pydantic.BaseModel):
    """Model representing a Strava stream."""

    type: StreamType
    data: list[float]


def _strava_request(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    """Make a request to the Strava API."""
    params = params or {}
    headers = {"Authorization": strava_config.get_bearer_token()}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def list_strava_activities(per_page: int = 2, page: int = 1) -> list[StravaActivity]:
    """List activities for the authenticated Strava athlete."""
    url = StravaEndpoint.ATHLETE_ACTIVITIES.value
    params = {"per_page": per_page, "page": page}
    response = _strava_request(url, params)
    return [StravaActivity(**activity) for activity in response.json()]


def get_strava_activity(activity_id: int) -> StravaActivity:
    """Get a specific Strava activity by ID."""
    url = StravaEndpoint.ACTIVITY.value.format(activity_id=activity_id)
    response = _strava_request(url)
    return StravaActivity(**response.json())


def get_strava_activity_streams(activity_id: int) -> list[Stream]:
    """Get all streams for a specific Strava activity by ID."""
    url = StravaEndpoint.ACTIVITY_STREAMS.value.format(activity_id=activity_id)
    response = _strava_request(url)
    return [Stream(**stream) for stream in response.json()]


def _check_stream_type(response_element: dict[str, Any], stream_type: StreamType) -> bool:
    """Check if a stream exists for a specific Strava activity by type."""
    return stream_type.value in response_element.values()


def _validate_stream_response(response: requests.Response, stream_type: StreamType) -> bool:
    """Validate the response from the Strava API."""
    response_data = response.json()

    # Handle single stream response
    if isinstance(response_data, dict) and _check_stream_type(response_data, stream_type):
        return True

    # Handle multiple streams response
    if isinstance(response_data, list) and any(_check_stream_type(stream, stream_type) for stream in response_data):
        return True

    raise ValueError(f"Stream type {stream_type.value} not found in response: {response_data}")


def _extract_stream_data(response_data: dict[str, Any] | list[dict[str, Any]], stream_type: StreamType) -> dict[str, Any]:
    """Extract stream data from the response."""
    if isinstance(response_data, dict):
        return response_data

    if isinstance(response_data, list):
        for stream in response_data:
            if stream.get("type") == stream_type.value:
                return stream

    raise ValueError(f"Could not extract {stream_type.value} data from response")


def get_strava_activity_stream_by_type(activity_id: int, stream_type: StreamType) -> Stream:
    """Get a specific stream for a Strava activity by type."""
    url = StravaEndpoint.ACTIVITY_STREAMS_BY_TYPE.value.format(activity_id=activity_id, stream_type=stream_type.value)
    response = _strava_request(url)

    # Validate the response contains the requested stream type
    _validate_stream_response(response, stream_type)

    # Extract the stream data
    stream_data = _extract_stream_data(response.json(), stream_type)

    return Stream(type=stream_type, data=stream_data["data"])


if __name__ == "__main__":
    # Test the list_strava_activities function
    activities = list_strava_activities()
    # print(activities)

    # Test the get_strava_activity function
    test_id = activities[0].id
    # print(get_strava_activity(test_id))

    # Test the get_strava_activity_streams function
    # print(get_strava_activity_streams(test_id))

    # Test the get_strava_activity_stream_by_type function
    print(get_strava_activity_stream_by_type(test_id, StreamType.HEARTRATE))
