from enum import StrEnum


class Provider(StrEnum):
    """Provider of the data."""

    STRAVA = "strava"
    COROS = "coros"


class StreamType(StrEnum):
    """Type of the stream."""

    DISTANCE = "distance"
    HEARTRATE = "heartrate"
    CADENCE = "cadence"
    WATTS = "watts"
    TEMP = "temp"
    MOVING = "moving"
    GRADE_SMOOTH = "grade_smooth"
    LATLNG = "latlng"
    ALTITUDE = "altitude"
    VELOCITY_SMOOTH = "velocity_smooth"
    TIME = "time"
