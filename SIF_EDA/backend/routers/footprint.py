"""
Footprint vs Edge endpoint.

Returns a list of traders along with a chosen footprint metric and an
edge metric. Footprint is proxied by `price_levels_per_volume` and
edge is proxied by ROI. The results can be used to draw a scatter
plot showing how market impact relates to profitability.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..database import get_db
from ..schemas import FootprintPoint, FootprintScatterResponse

router = APIRouter(prefix="/footprint", tags=["footprint"])


@router.get("/scatter", response_model=FootprintScatterResponse)
async def get_footprint_scatter(
    limit: int = Query(500, ge=10, le=5000, description="Maximum number of points to return"),
    db: AsyncSession = Depends(get_db),
) -> FootprintScatterResponse:
    """Return a list of (footprint, edge) points for scatter plotting."""
    result = await db.execute(
        text(
            """
            SELECT
                trader,
                price_levels_per_volume AS footprint,
                roi                    AS edge
            FROM trader_agg
            WHERE price_levels_per_volume IS NOT NULL
              AND roi IS NOT NULL
            ORDER BY ABS(trader_pnl) DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )
    points: List[FootprintPoint] = []
    for r in result:
        points.append(
            FootprintPoint(
                trader=r.trader,
                footprint=float(r.footprint),
                edge=float(r.edge),
            )
        )
    return FootprintScatterResponse(points=points)