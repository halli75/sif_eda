"""
Archetypes endpoint.

This implementation provides a simple placeholder grouping of traders
into archetypes based on their labels. Each unique label becomes an
archetype containing all traders with that label. In future work you
can replace this logic with clustering on behavioural features to
identify more nuanced archetypes (e.g. momentum traders, event snipers).
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..database import get_db
from ..schemas import ArchetypesResponse, ArchetypeItem

router = APIRouter(prefix="/archetypes", tags=["archetypes"])


@router.get("/map", response_model=ArchetypesResponse)
async def get_archetypes(db: AsyncSession = Depends(get_db)) -> ArchetypesResponse:
    """
    Return a list of archetypes derived from trader labels. Each
    archetype contains the list of trader identifiers belonging to that
    label. If no labels exist the result is empty.
    """
    result = await db.execute(
        text(
            """
            SELECT COALESCE(trader_label, 'Unknown') AS label,
                   ARRAY_AGG(trader) AS members
            FROM trader_agg
            GROUP BY COALESCE(trader_label, 'Unknown')
            ORDER BY label
            """
        )
    )
    archetypes: List[ArchetypeItem] = []
    idx = 1
    for r in result:
        archetypes.append(
            ArchetypeItem(
                id=idx,
                name=r.label,
                members=r.members,
            )
        )
        idx += 1
    return ArchetypesResponse(archetypes=archetypes)