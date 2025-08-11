from .base import BaseConverter
from stride.stridedb.models import Stream, StreamEntry, Activity, StreamType, Provider
from stride.provider.strava.models import StravaJSONStreamDataResponseModel, StravaActivityResponseModel, StravaStreamType, StravaJSONStreamResponseModel


class StravaConverter(BaseConverter):
    """Converts Strava raw data to unified stridedb format."""

    # Map Strava stream types to unified types
    STREAM_TYPE_MAPPING = {
        StravaStreamType.HEARTRATE: StreamType.HEARTRATE,
        StravaStreamType.DISTANCE: StreamType.DISTANCE,
    }

    def to_stream(self, raw_stream: StravaJSONStreamDataResponseModel) -> Stream:
        """Convert Strava stream data to unified Stream model.

        Args:
            raw_stream: StravaJSONStreamDataResponseModel instance

        Returns:
            Unified Stream model
        """
        # Map stream type
        unified_stream_type = self.STREAM_TYPE_MAPPING.get(
            raw_stream.stream_type,
            raw_stream.stream_type,  # fallback to original
        )

        # Create stream entries
        stream_entries = [StreamEntry(index=index, stream_type=unified_stream_type, stream_entry=value) for index, value in enumerate(raw_stream.stream_data)]

        return Stream(stream_type=unified_stream_type, stream_entries=stream_entries)

    def to_activity(self, raw_activity: StravaActivityResponseModel) -> Activity:
        """Convert Strava activity to unified Activity model.

        Args:
            raw_activity: StravaActivityResponseModel instance

        Returns:
            Unified Activity model
        """
        return Activity(provider_activity_id=raw_activity.id, provider=Provider.STRAVA, distance=raw_activity.distance, moving_time=raw_activity.moving_time, duration=raw_activity.elapsed_time)

    def to_streams(self, raw_streams: StravaJSONStreamResponseModel) -> list[Stream]:
        """Convert multiple Strava streams to unified Stream models."""
        return [self.to_stream(raw_stream) for raw_stream in raw_streams.streams]
