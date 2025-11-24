"""API request and response schemas."""
from .message import (
    MessageGenerationRequest,
    MessageGenerationResponse,
    BriefingData,
    SegmentContext,
    AlternateMessage
)

from .crm import (
    ConstituentCreate,
    ConstituentUpdate,
    ConstituentResponse,
    ContributionCreate,
    ContributionUpdate,
    ContributionResponse,
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    DashboardStats
)

__all__ = [
    "MessageGenerationRequest",
    "MessageGenerationResponse",
    "BriefingData",
    "SegmentContext",
    "AlternateMessage",
    # CRM schemas
    "ConstituentCreate",
    "ConstituentUpdate",
    "ConstituentResponse",
    "ContributionCreate",
    "ContributionUpdate",
    "ContributionResponse",
    "InteractionCreate",
    "InteractionUpdate",
    "InteractionResponse",
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityResponse",
    "DashboardStats"
]
