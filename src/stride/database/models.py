import sqlmodel
import enum
from datetime import datetime
from pydantic import ConfigDict, model_validator, computed_field, Field
from typing import Any


# cascade is on the Relationship, not the Field: one the one side
# ondelete is on the Field, not the Relationship: on the many side
# use alias if the field name returned by the API is different from the field name you want in the model

StreamDataType = float


class StreamType(enum.StrEnum):
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


class Activity(sqlmodel.SQLModel, table=True):
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

    # relationship to the Stream table
    streams: list["Stream"] | None = sqlmodel.Relationship(back_populates="activity", cascade_delete=True)


class Stream(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    stream_type: StreamType = Field(alias="type")

    # relationship to the StreamEntry table
    stream_entries: list["StreamEntry"] | None = sqlmodel.Relationship(back_populates="stream", cascade_delete=True)

    # relationship to the Activity table
    # ondelete="CASCADE" means that if the activity is deleted, all streams will be deleted
    activity_id: int | None = sqlmodel.Field(foreign_key="activity.id", ondelete="CASCADE")  # generated when the session is committed
    activity: Activity | None = sqlmodel.Relationship(back_populates="streams")


class StreamEntry(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    index: int
    stream_type: StreamType = Field(alias="type")
    stream_entry: StreamDataType = Field(alias="data")

    # relationship to the Stream table
    # ondelete="CASCADE" means that if the stream is deleted, all stream entries will be deleted
    stream_id: int | None = sqlmodel.Field(foreign_key="stream.id", ondelete="CASCADE")  # generated when the session is committed
    stream: Stream | None = sqlmodel.Relationship(back_populates="stream_entries")


class JSONStreamData(sqlmodel.SQLModel, table=False):
    """Model for parsing individual stream data from Strava API JSON."""

    stream_type: StreamType = Field(alias="type")
    stream_data: list[float] = Field(alias="data")  # Keep as list[float] for JSON parsing

    @computed_field
    @property
    def stream_entries(self) -> list[StreamEntry]:
        """Convert this JSON stream data to StreamEntry objects."""
        return [
            StreamEntry(index=index, stream_type=self.stream_type, stream_entry=stream_entry)
            for index, stream_entry in enumerate(self.stream_data)
        ]


class JSONStreamResponseModel(sqlmodel.SQLModel, table=False):
    """Model representing a JSON response from the Strava API."""

    raw_streams: list[JSONStreamData]

    @model_validator(mode="before")
    def model_validator(cls, data: Any) -> dict[str, Any]:
        """Validate and transform the input data."""
        if isinstance(data, dict) and "raw_streams" in data:
            return data

        # Convert single dict to list if necessary
        streams = [data] if isinstance(data, dict) else data
        return {"raw_streams": streams}

    # TODO: is there a cleaner way to do this?
    # NOTE: difficulty is in going from a list of floats (JSONStreamData) to a list of StreamEntry objects in the JSONStreamResponseModel -> Stream conversion
    # NOTE: maybe using the before validator to convert the JSONStreamData.data to a list of StreamEntry objects?
    @computed_field
    @property
    def streams(self) -> dict[StreamType, Stream]:
        """Get all streams from the response."""
        return {stream.stream_type: Stream(stream_type=stream.stream_type, data=stream.stream_entries) for stream in self.raw_streams}

    def get_stream(self, stream_type: StreamType) -> Stream:
        """Get a stream from the response by type."""
        if stream_type not in self.streams:
            raise ValueError(f"Stream {stream_type} not found in streams: {self.streams.keys()}")
        return self.streams[stream_type]
