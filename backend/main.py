"""
FastAPI application entry point.

Main application setup with routes, middleware, and static file serving.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db
from .routes import (
    trip_router,
    activity_router,
    family_member_router,
    weather_router,
    geocoding_router,
)
from .routes.search import router as search_router
from .routes.voting import router as voting_router
from .routes.favorites import router as favorites_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Family Trip Planner application...")
    init_db()
    logger.info("Database initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down Family Trip Planner application...")


# Create FastAPI application
app = FastAPI(
    title="Family Trip Planner API",
    description="A collaborative family trip planning application with weather and mapping integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Include API routers
app.include_router(trip_router)
app.include_router(activity_router)
app.include_router(family_member_router)
app.include_router(weather_router)
app.include_router(geocoding_router)
app.include_router(search_router)
app.include_router(voting_router)
app.include_router(favorites_router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Family Trip Planner"}
    )


@app.get("/daily-planner", response_class=HTMLResponse)
async def daily_planner(request: Request):
    """Serve the daily planner page."""
    return templates.TemplateResponse(
        "daily_planner.html", {
            "request": request, 
            "title": "Daily Planner",
            "google_places_api_key": settings.google_places_api_key
        }
    )


@app.get("/map", response_class=HTMLResponse)
async def map_view(request: Request):
    """Serve the map view page."""
    return templates.TemplateResponse(
        "map.html", {"request": request, "title": "Trip Map"}
    )


@app.get("/discovery", response_class=HTMLResponse)
async def discovery_hub(request: Request):
    """Serve the activity discovery hub page."""
    return templates.TemplateResponse(
        "discovery_hub.html", {"request": request, "title": "Activity Discovery"}
    )


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon.ico from static files."""
    from fastapi.responses import FileResponse

    return FileResponse("frontend/static/favicon.ico")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0", "debug": settings.debug}


@app.get("/api/status")
async def api_status():
    """API status endpoint with service health checks."""

    # Test basic functionality
    weather_available = bool(settings.openweather_api_key)
    geocoding_available = True  # Nominatim doesn't require API key
    search_available = bool(settings.google_places_api_key)

    return {
        "api_version": "1.0.0",
        "services": {
            "weather": {
                "available": weather_available,
                "api_key_configured": weather_available,
            },
            "geocoding": {
                "available": geocoding_available,
                "provider": "Nominatim (OpenStreetMap)",
            },
            "search": {
                "available": search_available,
                "google_places_key_configured": search_available,
            },
        },
        "database": {"type": "SQLite", "url": settings.database_url},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
