import sqlmodel
from pydantic import Field, computed_field
import rich.repr

from stride.enums import Provider, StreamType

StreamDataType = float


class Activity(sqlmodel.SQLModel, table=True):
    """Activity model."""

    id: int = sqlmodel.Field(primary_key=True)
    provider: Provider = sqlmodel.Field(default=Provider.STRAVA)
    provider_activity_id: int = sqlmodel.Field(unique=True)
    distance: float = sqlmodel.Field(default=0.0)
    moving_time: int = sqlmodel.Field(default=0)
    duration: int = sqlmodel.Field(default=0)

    # relationship to the Stream table
    streams: list["Stream"] | None = sqlmodel.Relationship(back_populates="activity", cascade_delete=True)

    def has_stream_type(self, stream_type: StreamType) -> bool:
        """Check if this activity has a stream of a given type."""
        if not self.streams:
            return False
        return any(stream.stream_type == stream_type for stream in self.streams)

    @computed_field
    @property
    def has_heartrate_stream(self) -> bool:
        """Check if this activity has a heartrate stream."""
        return self.has_stream_type(StreamType.HEARTRATE)

    @computed_field
    @property
    def has_watts_stream(self) -> bool:
        """Check if this activity has a watts stream."""
        return self.has_stream_type(StreamType.WATTS)

    @computed_field
    @property
    def has_temp_stream(self) -> bool:
        """Check if this activity has a temp stream."""
        return self.has_stream_type(StreamType.TEMP)

    @computed_field
    @property
    def has_cadence_stream(self) -> bool:
        """Check if this activity has a cadence stream."""
        return self.has_stream_type(StreamType.CADENCE)

    @computed_field
    @property
    def has_distance_stream(self) -> bool:
        """Check if this activity has a distance stream."""
        return self.has_stream_type(StreamType.DISTANCE)

    @computed_field
    @property
    def has_time_stream(self) -> bool:
        """Check if this activity has a time stream."""
        return self.has_stream_type(StreamType.TIME)

    @computed_field
    @property
    def has_latlng_stream(self) -> bool:
        """Check if this activity has a latlng stream."""
        return self.has_stream_type(StreamType.LATLNG)

    @computed_field
    @property
    def has_altitude_stream(self) -> bool:
        """Check if this activity has an altitude stream."""
        return self.has_stream_type(StreamType.ALTITUDE)

    @computed_field
    @property
    def has_grade_smooth_stream(self) -> bool:
        """Check if this activity has a grade_smooth stream."""
        return self.has_stream_type(StreamType.GRADE_SMOOTH)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "id", self.id
        yield "provider", self.provider
        yield "provider_activity_id", self.provider_activity_id
        yield "distance", self.distance
        yield "moving_time", self.moving_time
        yield "duration", self.duration
        yield "has_heartrate_stream", self.has_heartrate_stream
        yield "has_watts_stream", self.has_watts_stream
        yield "has_temp_stream", self.has_temp_stream
        yield "has_cadence_stream", self.has_cadence_stream
        yield "has_distance_stream", self.has_distance_stream
        yield "has_time_stream", self.has_time_stream
        yield "has_latlng_stream", self.has_latlng_stream
        yield "has_altitude_stream", self.has_altitude_stream
        yield "has_grade_smooth_stream", self.has_grade_smooth_stream


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
