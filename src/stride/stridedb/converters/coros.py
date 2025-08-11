from typing import List, Any
from .base import BaseConverter
from stride.stridedb.models import Stream, Activity


class CorosConverter(BaseConverter):
    """Converts Coros raw data to unified stridedb format."""

    def to_stream(self, raw_stream: Any) -> Stream:
        """Convert Coros stream data to unified Stream model."""
        # TODO: Implement when Coros integration is added
        raise NotImplementedError("Coros converter not yet implemented")

    def to_activity(self, raw_activity: Any) -> Activity:
        """Convert Coros activity to unified Activity model."""
        # TODO: Implement when Coros integration is added
        raise NotImplementedError("Coros converter not yet implemented")

    def to_streams(self, raw_streams: List[Any]) -> List[Stream]:
        """Convert multiple Coros streams to unified Stream models."""
        return [self.to_stream(raw_stream) for raw_stream in raw_streams]
