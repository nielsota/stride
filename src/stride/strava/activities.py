import enum
import pydantic
from datetime import datetime
from typing import Optional, Any
from loguru import logger

from stride.config import strava_config
from stride.connections.strava import StravaEndpoint

import requests  # type: ignore

StreamDataType = float | bool | None
ResponseType = dict[str, Any]


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
    data: list[StreamDataType]

    @pydantic.computed_field  # type: ignore[prop-decorator]
    @property
    def stream_length(self) -> int:
        """Get the length of the stream."""
        return len(self.data)


class VelocitySmoothStream(Stream):
    """Model representing a Strava velocity smooth stream."""

    type: StreamType = StreamType.VELOCITY_SMOOTH

    @pydantic.computed_field  # type: ignore[prop-decorator]
    @property
    def velocity_kmh(self) -> list[StreamDataType]:
        """Convert velocity from m/s to km/h."""
        return [round(v * 3.6, 2) if v is not None else None for v in self.data]


class JSONStreamResponseModel(pydantic.BaseModel):
    """Model representing a JSON response from the Strava API."""

    streams: list[Stream]

    # TODO: Ask Pim about this: why is the input already a stream?
    # TODO: Why does it contain the streams key even though the response does not?
    @pydantic.model_validator(mode="before")
    def model_validator(cls, data: list[Stream] | Stream) -> dict[str, list[Stream]]:
        """Validate and transform the input data."""
        if isinstance(data, dict) and "streams" in data:
            return data

        # Convert single Stream to list if necessary
        streams = [data] if isinstance(data, Stream) else data
        return {"streams": streams}

    @property
    def all_streams(self) -> dict[StreamType, Stream]:
        """Get all streams from the response."""
        return {stream.type: stream for stream in self.streams}

    def get_stream_by_type(self, stream_type: StreamType) -> Stream:
        """Get a stream from the response by type."""
        return self.all_streams[stream_type]


StreamTypeToStream: dict[StreamType, type[Stream]] = {
    StreamType.TIME: Stream,
    StreamType.DISTANCE: Stream,
    StreamType.LATLNG: Stream,
    StreamType.ALTITUDE: Stream,
    StreamType.VELOCITY_SMOOTH: VelocitySmoothStream,
    StreamType.HEARTRATE: Stream,
    StreamType.CADENCE: Stream,
    StreamType.WATTS: Stream,
    StreamType.TEMP: Stream,
    StreamType.MOVING: Stream,
    StreamType.GRADE_SMOOTH: Stream,
}


def _strava_request(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    """Make a request to the Strava API."""
    params = params or {}
    logger.debug(f"Making request to {url} with params {params}")
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


def get_strava_activity_stream_by_type(activity_id: int, stream_type: StreamType) -> Stream:
    """Get a specific stream for a Strava activity by type."""
    logger.debug(f"Getting {stream_type.value} stream for activity {activity_id}")
    url = StravaEndpoint.ACTIVITY_STREAMS_BY_TYPE.value.format(activity_id=activity_id, stream_type=stream_type.value)
    print(_strava_request(url).json())
    stream_response = JSONStreamResponseModel(streams=_strava_request(url).json())

    # Extract the stream data
    stream_data = stream_response.get_stream_by_type(stream_type)
    logger.debug(f"sample of {stream_type.value} stream data: {stream_data.data[:10]}")

    return stream_data


def get_strava_activity_streams(activity_id: int) -> list[Stream]:
    """Get all streams for a specific Strava activity by ID."""
    streams = []
    for stream_type in StreamType:
        try:
            stream = get_strava_activity_stream_by_type(activity_id, stream_type)
            streams.append(stream)
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to retrieve {stream_type.value} stream for activity {activity_id}: {str(e)[:100]}...")
    return streams


if __name__ == "__main__":
    # Test the list_strava_activities function
    activities = list_strava_activities()
    # print(activities)

    # Test the get_strava_activity function
    test_id = activities[1].id
    # print(get_strava_activity(test_id))

    # Test the get_strava_activity_streams function
    # print(get_strava_activity_streams(test_id))

    # Test the get_strava_activity_stream_by_type function
    get_strava_activity_stream_by_type(test_id, StreamType.HEARTRATE)
    # print(get_strava_activity_stream_by_type(test_id, StreamType.DISTANCE))
    # print(get_strava_activity_stream_by_type(test_id, StreamType.VELOCITY_SMOOTH))

    # Test the get_strava_activity_streams function
    # get_strava_activity_streams(test_id)
