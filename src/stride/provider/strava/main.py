import requests
import datetime
from loguru import logger
from typing import Any
from stride.config import get_strava_config
from stride.constants import DAYS_IN_MONTH, MAX_ACTIVITIES_PER_DAY

from stride.provider.strava.endpoints import StravaEndpoints
from stride.provider.strava.models import (
    StravaActivityResponseModel,
    StravaJSONStreamDataResponseModel,
    StravaJSONStreamResponseModel,
    StravaStreamType,
)

strava_config = get_strava_config()


class StravaService:
    """Service for interacting with the Strava API."""

    def __init__(self):
        self.config = get_strava_config()

    def _generic_request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Make a request to the Strava API.

        Wraps some common functionality for making requests to the Strava API.

        Args:
            url: The URL to make the request to.
            params: The parameters to pass to the request.

        Returns:
            requests.Response object.
        """
        params = params or {}
        logger.debug(f"Making request to {url} with params {params}")
        headers = {"Authorization": self.config.get_bearer_token()}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def _split_date_range(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        split_by: str = "month",
    ) -> list[tuple[datetime.datetime, datetime.datetime]]:
        """Split the before and after date range into months."""
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")
        match split_by:
            case "month":
                return [
                    (
                        start_date - datetime.timedelta(days=i * DAYS_IN_MONTH),
                        max(start_date - datetime.timedelta(days=(i + 1) * DAYS_IN_MONTH), end_date),
                    )
                    for i in range(((end_date - start_date).days // DAYS_IN_MONTH) + 1)
                ]
            case "day":
                return [
                    (
                        start_date - datetime.timedelta(days=i),
                        start_date - datetime.timedelta(days=(i + 1)),
                    )
                    for i in range(((end_date - start_date).days) + 1)
                ]
            case _:
                raise ValueError(f"Invalid split_by: {split_by}, must be 'month' or 'day'")

    def get_activities(
        self,
        per_page: int = DAYS_IN_MONTH,
        page: int = 1,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
    ) -> list[StravaActivityResponseModel]:
        """List activities for the authenticated Strava athlete.

        Args:
            per_page: Number of activities to return per page.
            page: Page number to return.
            after: Filter activities after this date.
            before: Filter activities before this date.

        Returns:
            List of StravaActivityResponseModel objects.
        """
        url = StravaEndpoints.ATHLETE_ACTIVITIES.value
        params = {
            "per_page": per_page,
            "page": page,
        }
        if start_date:
            params["after"] = start_date.timestamp()
        if end_date:
            params["before"] = end_date.timestamp()
        response = self._generic_request(url, params)
        activities = [StravaActivityResponseModel(**activity) for activity in response.json()]
        return activities

    def get_activities_by_date_range(
        self,
        start_date: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=365),
        end_date: datetime.datetime = datetime.datetime.now(),
    ) -> list[StravaActivityResponseModel]:
        """Get activities for a given date range.

        Args:
            after: Filter activities after this date (default: 1 year ago).
            before: Filter activities before this date (default: today).

        Returns:
            List of StravaActivityResponseModel objects.
        """
        months = self._split_date_range(start_date, end_date, split_by="month")
        logger.debug(f"Splitting date range into: {months}")
        activities = [
            activity
            for start_date, end_date in months
            for activity in self.get_activities(
                start_date=start_date,
                end_date=end_date,
                per_page=MAX_ACTIVITIES_PER_DAY * DAYS_IN_MONTH,
            )
        ]
        return activities

    def get_activity(
        self,
        activity_id: int,
    ) -> StravaActivityResponseModel:
        """Get a specific activity for the authenticated Strava athlete.

        Args:
            activity_id: The ID of the activity to get.

        Returns:
            StravaActivityResponseModel object.
        """
        url = StravaEndpoints.ACTIVITY.value.format(activity_id=activity_id)
        response = self._generic_request(url)
        return StravaActivityResponseModel(**response.json())

    def is_latest_activity_in_database(
        self,
        activity_id: int,
    ) -> bool:
        """Check if the latest activity is in the database.

        NOTE: this is a hack to get the latest activity from the database.
        It's not a good idea to do this, but it's a quick way to get the latest activity from the database.
        TODO: use a better way to get the latest activity from the database.

        Args:
            activity_id: The ID of the activity to check.

        Returns:
            True if the latest activity is in the database, False otherwise.
        """
        latest_activity = self.get_activities(per_page=1, page=1)[0]
        return latest_activity.id == activity_id

    def get_stream(
        self,
        activity_id: int,
        stream_type: StravaStreamType,
    ) -> StravaJSONStreamDataResponseModel:
        """Get a specific stream for a Strava activity by type.

        Args:
            activity_id: The ID of the activity to get the stream for.
            stream_type: The type of stream to get.

        Returns:
            StravaJSONStreamDataResponseModel object.
        """
        logger.debug(f"Getting {stream_type.value} stream for activity {activity_id}")
        url = StravaEndpoints.ACTIVITY_STREAMS_BY_TYPE.value.format(activity_id=activity_id, stream_type=stream_type.value)
        stream_response = StravaJSONStreamResponseModel(streams=self._generic_request(url).json())
        return stream_response

    def get_streams(
        self,
        activity_id: int,
        stream_types: list[StravaStreamType] = [
            StravaStreamType.HEARTRATE,
            StravaStreamType.DISTANCE,
            StravaStreamType.TIME,
            StravaStreamType.VELOCITY_SMOOTH,
        ],
    ) -> list[StravaJSONStreamDataResponseModel]:
        """Get all streams for a Strava activity.

        Args:
        activity_id: The ID of the activity to get streams for.
        stream_types: The types of streams to get.

        Returns:
            List of StravaJSONStreamDataResponseModel objects.
        """
        logger.debug(f"Getting all streams for activity {activity_id}")
        return sum(
            [self.get_stream(activity_id, stream_type) for stream_type in stream_types],
            start=StravaJSONStreamResponseModel(streams=[]),
        )
