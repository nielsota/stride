import sqlmodel
import enum
import rich.repr
from datetime import datetime
from pydantic import ConfigDict, model_validator, Field
from typing import Any

StravaStreamDataType = float


class StravaStreamType(enum.StrEnum):
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


class StravaAccessTokenResponse(sqlmodel.SQLModel, table=False):
    """Response from the Strava API when refreshing an access token."""

    token_type: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    expires_in: int


class StravaActivityResponseModel(sqlmodel.SQLModel, table=False):
    """Model representing a Strava activity."""

    # Enable automatic datetime parsing from strings
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, arbitrary_types_allowed=True)

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
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
    average_heartrate: float | None = None
    max_heartrate: float | None = None
    elev_high: float | None = None  # in meters
    elev_low: float | None = None  # in meters
    description: str | None = None
    calories: float | None = None
    has_heartrate: bool = False
    average_cadence: float | None = None
    average_watts: float | None = None
    max_watts: float | None = None
    weighted_average_watts: float | None = None
    kilojoules: float | None = None
    device_watts: bool | None = None
    average_temp: float | None = None
    suffer_score: int | None = None


class StravaJSONStreamDataResponseModel(sqlmodel.SQLModel, table=False):
    """Model for parsing individual stream data from Strava API JSON."""

    stream_type: StravaStreamType = Field(alias="type")
    stream_data: list[float] = Field(alias="data")  # Keep as list[float] for JSON parsing

    def __rich_repr__(self) -> rich.repr.Result:
        yield "stream_type", self.stream_type.value
        yield "stream_data", (str(self.stream_data[:10]) + "..." if len(self.stream_data) > 10 else str(self.stream_data))


# NOTE: if I change streams to raw_streams, the model validator will break, why?
class StravaJSONStreamResponseModel(sqlmodel.SQLModel, table=False):
    """Model representing a JSON response from the Strava API."""

    streams: list[StravaJSONStreamDataResponseModel]

    @model_validator(mode="before")
    def model_validator(cls, data: Any) -> dict[str, Any]:
        """Validate and transform the input data."""
        if isinstance(data, dict) and "streams" in data:
            return data

        # Convert single dict to list if necessary
        streams = [data] if isinstance(data, dict) else data
        return {"streams": streams}

    def __contains__(self, other: "StravaJSONStreamResponseModel") -> bool:
        """Check if a StravaJSONStreamResponseModel is contained in another."""
        return any(stream.stream_type == other.stream_type for stream in self.streams)

    def __add__(self, other: "StravaJSONStreamResponseModel") -> "StravaJSONStreamResponseModel":
        """Add two StravaJSONStreamResponseModel objects together."""
        return StravaJSONStreamResponseModel(streams=([stream for stream in self.streams if stream not in other.streams] + other.streams))
