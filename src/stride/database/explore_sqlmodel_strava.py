import sqlmodel
import enum

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
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    username: str
    streams: list["Stream"] = sqlmodel.Relationship(back_populates="activity")


class Stream(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    stream_type: StreamType

    # relationship to the StreamEntry table
    stream_entries: list["StreamEntry"] = sqlmodel.Relationship(back_populates="stream")

    # relationship to the Activity table
    activity_id: int | None = sqlmodel.Field(foreign_key="activity.id")
    activity: Activity | None = sqlmodel.Relationship(back_populates="streams")


class StreamEntry(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    activity_id: int
    index: int
    stream_type: StreamType
    data: StreamDataType

    # relationship to the Stream table
    stream_id: int | None = sqlmodel.Field(foreign_key="stream.id")
    stream: Stream | None = sqlmodel.Relationship(back_populates="stream_entries")


sqllite_url = "sqlite:///database.db"

# handles communication with the database
engine = sqlmodel.create_engine(sqllite_url)


# creaetes database.db file, and adds tables to it
def create_database() -> None:
    sqlmodel.SQLModel.metadata.create_all(engine)


def create_stream_entries() -> None:
    # same activity_id, same stream_type
    stream_entry_11 = StreamEntry(activity_id=1, index=0, stream_type=StreamType.TIME, data=1)
    stream_entry_12 = StreamEntry(activity_id=1, index=1, stream_type=StreamType.TIME, data=2)
    stream_entry_13 = StreamEntry(activity_id=1, index=2, stream_type=StreamType.TIME, data=3)

    # same activity_id, different stream_type
    stream_entry_21 = StreamEntry(activity_id=1, index=0, stream_type=StreamType.VELOCITY_SMOOTH, data=2)
    stream_entry_22 = StreamEntry(activity_id=1, index=1, stream_type=StreamType.VELOCITY_SMOOTH, data=3)
    stream_entry_23 = StreamEntry(activity_id=1, index=2, stream_type=StreamType.VELOCITY_SMOOTH, data=2)

    time_stream = Stream(activity_id=1, stream_type=StreamType.TIME, stream_data=[stream_entry_11, stream_entry_12, stream_entry_13])
    velocity_stream = Stream(activity_id=1, stream_type=StreamType.VELOCITY_SMOOTH, stream_data=[stream_entry_21, stream_entry_22, stream_entry_23])

    activity = Activity(username="John Doe", streams=[time_stream, velocity_stream])

    with sqlmodel.Session(engine) as session:
        session.add(activity)
        session.commit()
        session.refresh(activity)
        print("Created activity: ", activity.streams)


def main() -> None:
    create_database()
    create_stream_entries()


if __name__ == "__main__":
    main()
