"""
Label audit endpoints.

The `/labels/summary` endpoint returns aggregated metrics per trader
label. It reports the number of traders, average profit per volume
(PPV), mean ROI and standard deviation of ROI. This helps evaluate
whether certain labels correspond to superior or inferior performance.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..database import get_db
from ..schemas import LabelSummaryItem, LabelSummaryResponse

router = APIRouter(prefix="/labels", tags=["labels"])


@router.get("/summary", response_model=LabelSummaryResponse)
async def get_label_summary(db: AsyncSession = Depends(get_db)) -> LabelSummaryResponse:
    """Return aggregated PPV and ROI statistics by trader label."""
    result = await db.execute(
        text(
            """
            SELECT
                COALESCE(trader_label, 'Unknown') AS label,
                COUNT(*)                        AS count,
                AVG(trader_ppv)                 AS avg_ppv,
                AVG(roi)                        AS roi_mean,
                STDDEV_POP(roi)                 AS roi_std
            FROM trader_agg
            GROUP BY COALESCE(trader_label, 'Unknown')
            ORDER BY count DESC
            """
        )
    )
    labels: List[LabelSummaryItem] = []
    for r in result:
        labels.append(
            LabelSummaryItem(
                label=r.label,
                count=r.count,
                avg_ppv=float(r.avg_ppv) if r.avg_ppv is not None else None,
                roi_mean=float(r.roi_mean) if r.roi_mean is not None else None,
                roi_std=float(r.roi_std) if r.roi_std is not None else None,
            )
        )
    return LabelSummaryResponse(labels=labels)