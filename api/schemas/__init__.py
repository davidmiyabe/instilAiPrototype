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
    DashboardStats,
    GivingSummary
)

__all__ = [
    # Message schemas
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
    "DashboardStats",
    "GivingSummary"
]
