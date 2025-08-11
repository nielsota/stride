import enum


class StravaEndpoints(str, enum.Enum):
    TOKEN = "https://www.strava.com/oauth/token"
    ATHLETE_ACTIVITIES = "https://www.strava.com/api/v3/athlete/activities"
    ACTIVITY = "https://www.strava.com/api/v3/activities/{activity_id}"
    ACTIVITY_STREAMS = "https://www.strava.com/api/v3/activities/{activity_id}/streams"
    ACTIVITY_STREAMS_BY_TYPE = "https://www.strava.com/api/v3/activities/{activity_id}/streams/{stream_type}"
