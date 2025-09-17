"""
Overview endpoints.

Provides a summary of the dataset: total counts, sums and a list of top
traders by absolute profit. The endpoint is deliberately simple and
should return quickly even on large datasets.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..database import get_db
from ..schemas import TraderSummary, OverviewResponse


router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/", response_model=OverviewResponse)
async def get_overview(db: AsyncSession = Depends(get_db)) -> OverviewResponse:
    """Return top level metrics and a list of top traders by PnL."""
    # Aggregate totals and average ROI
    result = await db.execute(
        text(
            """
            SELECT
                COUNT(*)                            AS total_traders,
                COALESCE(SUM(trader_volume), 0)     AS total_volume,
                COALESCE(SUM(trader_pnl), 0)        AS total_pnl,
                AVG(roi)                            AS average_roi
            FROM trader_agg
            """
        )
    )
    row = result.one()
    total_traders = row.total_traders or 0
    total_volume = float(row.total_volume or 0)
    total_pnl = float(row.total_pnl or 0)
    average_roi = float(row.average_roi) if row.average_roi is not None else None

    # Fetch top 10 traders by absolute profit
    top_result = await db.execute(
        text(
            """
            SELECT trader, trader_pnl, roi, trader_volume, trader_label
            FROM trader_agg
            ORDER BY ABS(trader_pnl) DESC
            LIMIT 10
            """
        )
    )
    top_traders: List[TraderSummary] = []
    for r in top_result:
        top_traders.append(
            TraderSummary(
                trader=r.trader,
                pnl=float(r.trader_pnl) if r.trader_pnl is not None else 0.0,
                roi=float(r.roi) if r.roi is not None else None,
                volume=float(r.trader_volume) if r.trader_volume is not None else None,
                label=r.trader_label,
            )
        )

    return OverviewResponse(
        total_traders=total_traders,
        total_volume=total_volume,
        total_pnl=total_pnl,
        average_roi=average_roi,
        top_traders=top_traders,
    )