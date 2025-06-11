import requests  # type: ignore[import-untyped]
from loguru import logger
from typing import Any
from stride.config import get_strava_config
from stride.strava.activities import StravaEndpoint
from stride.database.database import create_database
from stride.database.models import Activity, Stream, StreamType, JSONStreamResponseModel, JSONStreamData

strava_config = get_strava_config()


def _strava_request(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    """Make a request to the Strava API."""
    params = params or {}
    logger.debug(f"Making request to {url} with params {params}")
    headers = {"Authorization": strava_config.get_bearer_token()}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def list_strava_activities(per_page: int = 2, page: int = 1, include_streams: list[StreamType] | None = None) -> list[Activity]:
    """List activities for the authenticated Strava athlete."""
    url = StravaEndpoint.ATHLETE_ACTIVITIES.value
    params = {"per_page": per_page, "page": page}
    response = _strava_request(url, params)
    activities = [Activity(**activity) for activity in response.json()]

    if include_streams:
        for activity in activities:
            activity.streams = get_strava_activity_streams(activity.id, include_streams)

    return activities


def get_strava_activity_stream_by_type(activity_id: int, stream_type: StreamType) -> Stream:
    """Get a specific stream for a Strava activity by type."""
    logger.debug(f"Getting {stream_type.value} stream for activity {activity_id}")
    url = StravaEndpoint.ACTIVITY_STREAMS_BY_TYPE.value.format(activity_id=activity_id, stream_type=stream_type.value)

    response = _strava_request(url)
    # TODO: why does this only work if I add the raw_streams key? Don't need to do this for the activities response
    stream_response = JSONStreamResponseModel(raw_streams=[JSONStreamData(**stream) for stream in response.json()])

    logger.debug(f"response: {response.json()}") # raw
    # logger.debug(f"stream_response: {stream_response}") # JSONStreamResponseModel, note the string "type" from raw response is converted to StreamType enum
    # logger.debug(f"stream_response.streams: {stream_response.streams}") # dict of StreamType -> Stream
    # TODO: how to convert JSONStreamData.data from list[float] to list[StreamEntry] objects? -> use computed_field in JSONStreamData to post-process the data into StreamEntry objects

    # Extract the stream data
    stream_data = stream_response.get_stream(stream_type)
    # logger.debug(f"sample of {stream_type.value} stream data: {stream_data.data[:10]}")

    return stream_data


def get_strava_activity_streams(activity_id: int, include_streams: list[StreamType] | None = None) -> list[Stream]:
    """Get all streams for a Strava activity."""
    streams = []
    for stream_type in include_streams:
        streams.append(get_strava_activity_stream_by_type(activity_id, stream_type))
    return streams


def main() -> None:
    create_database()
    activities = list_strava_activities(per_page=1, page=1, include_streams=[StreamType.VELOCITY_SMOOTH])
    logger.debug(f"activities: {activities}")

    # activity_id = activities[0].id
    # stream_data = get_strava_activity_stream_by_type(activity_id, StreamType.VELOCITY_SMOOTH)

    # with sqlmodel.Session(engine) as session:
    #    session.add_all(activities)
    #    session.commit()


if __name__ == "__main__":
    main()
