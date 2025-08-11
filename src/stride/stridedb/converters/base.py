from abc import ABC, abstractmethod
from typing import Any, List
from stride.stridedb.models import Activity, Stream


class BaseConverter(ABC):
    """Abstract base class for data converters."""

    @abstractmethod
    def to_stream(self, data: Any) -> Stream:
        """Convert raw stream data to unified Stream model."""
        pass

    @abstractmethod
    def to_activity(self, data: Any) -> Activity:
        """Convert raw activity data to unified Activity model."""
        pass

    @abstractmethod
    def to_streams(self, data: List[Any]) -> List[Stream]:
        """Convert multiple raw streams to unified Stream models."""
        pass
