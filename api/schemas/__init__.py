"""API request and response schemas."""
from .message import (
    MessageGenerationRequest,
    MessageGenerationResponse,
    BriefingData,
    SegmentContext,
    AlternateMessage
)

__all__ = [
    "MessageGenerationRequest",
    "MessageGenerationResponse",
    "BriefingData",
    "SegmentContext",
    "AlternateMessage"
]
