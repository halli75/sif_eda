"""
Subpackage initialiser for routers. Each router module exposes a
`router` object that can be included in the FastAPI app. This file
provides a convenient list of all routers for inclusion in main.py.
"""
from .overview import router as overview_router
from .labels import router as labels_router
from .footprint import router as footprint_router
from .topics import router as topics_router
from .archetypes import router as archetypes_router

__all__ = [
    "overview_router",
    "labels_router",
    "footprint_router",
    "topics_router",
    "archetypes_router",
]