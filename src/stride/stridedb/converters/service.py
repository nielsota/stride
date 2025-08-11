from typing import List, Any
from stride.stridedb.converters import ConverterFactory
from stride.stridedb.models import Activity, Provider


class StrideConverterService:
    """High-level service for processing activity data from various sources."""

    @staticmethod
    def process_activity_data(provider: Provider, raw_activity: Any, raw_streams: List[Any]) -> Activity:
        """Generic method to process activity data from any source.

        Args:
            source: Data source (STRAVA, COROS, etc.)
            raw_activity: Raw activity data
            raw_streams: List of raw stream data

        Returns:
            Unified Activity model with streams
        """
        converter = ConverterFactory.get_converter(provider)

        activity = converter.to_activity(raw_activity)
        streams = converter.to_streams(raw_streams)
        activity.streams = streams

        return activity

    @staticmethod
    def process_strava_data(raw_activity: Any, raw_streams: List[Any]) -> Activity:
        """Process raw Strava data into unified format.

        Args:
            raw_activity: Raw Strava activity data
            raw_streams: List of raw Strava stream data

        Returns:
            Unified Activity model with streams
        """
        return StrideConverterService.process_activity_data(Provider.STRAVA, raw_activity, raw_streams)

    @staticmethod
    def process_coros_data(raw_activity: Any, raw_streams: List[Any]) -> Activity:
        """Process raw Coros data into unified format.

        Args:
            raw_activity: Raw Coros activity data
            raw_streams: List of raw Coros stream data

        Returns:
            Unified Activity model with streams
        """
        # TODO: uncomment when Coros is added
        raise NotImplementedError("Coros processing not yet implemented")
        # return StrideConverterService.process_activity_data(Provider.COROS, raw_activity, raw_streams)
