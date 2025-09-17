"""
Entry point for the FastAPI application.

This module instantiates the FastAPI app and includes all routers
defined in the `backend.routers` package. It also configures CORS to
allow requests from any origin during development. Adjust the CORS
settings as needed for production use.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    overview_router,
    labels_router,
    footprint_router,
    topics_router,
    archetypes_router,
)


def create_app() -> FastAPI:
    app = FastAPI(title="Polymarket Trader Explorer API", version="0.1.0")
    # Allow all origins for ease of development. In production you
    # should restrict origins to trusted domains.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Register routers
    app.include_router(overview_router)
    app.include_router(labels_router)
    app.include_router(footprint_router)
    app.include_router(topics_router)
    app.include_router(archetypes_router)
    return app


app = create_app()