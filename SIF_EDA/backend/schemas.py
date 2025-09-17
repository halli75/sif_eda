"""
Pydantic schemas for API responses.

Using schemas documents the API contract and allows FastAPI to
automatically generate OpenAPI documentation. These models are kept
minimal to avoid coupling the API too tightly to the underlying database
schema; additional fields can be added later as needed.
"""
from typing import List, Optional
from pydantic import BaseModel


class TraderSummary(BaseModel):
    trader: str
    pnl: float
    roi: Optional[float]
    volume: Optional[float]
    label: Optional[str]


class OverviewResponse(BaseModel):
    total_traders: int
    total_volume: float
    total_pnl: float
    average_roi: Optional[float]
    top_traders: List[TraderSummary]


class LabelSummaryItem(BaseModel):
    label: str
    count: int
    avg_ppv: Optional[float]
    roi_mean: Optional[float]
    roi_std: Optional[float]


class LabelSummaryResponse(BaseModel):
    labels: List[LabelSummaryItem]


class FootprintPoint(BaseModel):
    trader: str
    footprint: float
    edge: float


class FootprintScatterResponse(BaseModel):
    points: List[FootprintPoint]


class TopicShare(BaseModel):
    topic: str
    share: float


class TraderTopicResponse(BaseModel):
    trader: str
    active_topics: int
    topic_entropy: float
    niche_score: float
    topic_shares: List[TopicShare]


class ArchetypeItem(BaseModel):
    id: int
    name: str
    members: List[str]


class ArchetypesResponse(BaseModel):
    archetypes: List[ArchetypeItem]