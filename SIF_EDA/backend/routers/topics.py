"""
Topic exploration endpoint.

For a given trader, return their topic distribution along with entropy
and niche score metrics. If the trader is not found the endpoint
returns a 404 error.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..database import get_db
from ..schemas import TopicShare, TraderTopicResponse

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/trader/{trader_id}", response_model=TraderTopicResponse)
async def get_trader_topics(
    trader_id: str = Path(..., description="Trader identifier"),
    db: AsyncSession = Depends(get_db),
) -> TraderTopicResponse:
    """Return the topic distribution and metrics for a specific trader."""
    # Fetch topic shares
    topic_result = await db.execute(
        text(
            """
            SELECT topic, share
            FROM trader_topic_share
            WHERE trader = :trader
            ORDER BY share DESC
            """
        ),
        {"trader": trader_id},
    )
    topics = [TopicShare(topic=r.topic, share=float(r.share)) for r in topic_result]
    # Fetch entropy and niche score
    metrics_result = await db.execute(
        text(
            """
            SELECT topic_entropy, niche_score, active_topics
            FROM trader_topic_metrics
            WHERE trader = :trader
            """
        ),
        {"trader": trader_id},
    )
    metrics_row = metrics_result.first()
    if metrics_row is None:
        # If no entry in trader_topic_metrics, check if trader exists at all
        check = await db.execute(
            text("SELECT 1 FROM trader_agg WHERE trader = :trader"), {"trader": trader_id}
        )
        if check.first() is None:
            raise HTTPException(status_code=404, detail="Trader not found")
        # Trader exists but has no topic info; return zeros
        return TraderTopicResponse(
            trader=trader_id,
            active_topics=0,
            topic_entropy=0.0,
            niche_score=1.0,
            topic_shares=topics,
        )
    return TraderTopicResponse(
        trader=trader_id,
        active_topics=metrics_row.active_topics,
        topic_entropy=float(metrics_row.topic_entropy),
        niche_score=float(metrics_row.niche_score),
        topic_shares=topics,
    )