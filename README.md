name: "Family Trip Planning Web App - FastAPI + SQLite Implementation"
description: |

## Purpose
Build a comprehensive family trip planning web application using FastAPI backend with SQLite database, HTML/CSS/JavaScript frontend, and external API integrations for weather and geocoding. This follows the MVP approach outlined in INITIAL.md with a focus on practical, family-friendly features.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Create a production-ready family trip planning web application where families can collaboratively plan their 7-day Osaka trip (July 27 - August 2, 2025) with daily activities, weather integration, map visualization, and budget tracking.

## Why
- **Business value**: Simplifies family travel planning with collaborative tools
- **Integration**: Demonstrates FastAPI + SQLite + external APIs best practices
- **Problems solved**: Eliminates scattered trip planning across multiple apps/documents
- **Family focused**: Simple interface that works for all family members

## What
A web application with:
- Daily itinerary planning with time slots (Morning, Afternoon, Evening)
- Family member preferences and wishlist management
- Interactive map with accommodation and activity locations
- Weather integration for daily planning
- Budget tracking and expense categories
- Export/print functionality for offline use

### Success Criteria
- [ ] Family members can add/edit activities for each day
- [ ] Interactive map shows accommodation and planned activities
- [ ] Weather data influences daily planning recommendations
- [ ] Budget tracking works across categories
- [ ] Mobile-responsive design works on all devices
- [ ] Export functionality generates printable itinerary

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://fastapi.tiangolo.com/tutorial/sql-databases/
  why: Official FastAPI + SQLAlchemy tutorial with SQLite setup
  
- url: https://github.com/zhanymkanov/fastapi-best-practices
  why: Comprehensive FastAPI best practices and project structure
  
- url: https://medium.com/@stefentaime_10958/geocoding-api-built-with-fastapi-and-the-nominatim-service-791f7764e87b
  why: FastAPI + Nominatim geocoding integration tutorial
  
- url: https://github.com/buche/leaflet-openweathermap
  why: Leaflet.js + OpenWeatherMap integration library
  
- url: https://leafletjs.com/examples.html
  why: Official Leaflet.js tutorials and examples
  
- url: https://openweathermap.org/api/weathermaps
  why: OpenWeatherMap API documentation and weather maps
  
- file: /mnt/d/AI program/context-engineering-intro/tests/test_geocoding.py
  why: Existing pattern for API integration testing with mocks
  
- file: /mnt/d/AI program/context-engineering-intro/tests/test_imaging.py
  why: HTTP client testing patterns and error handling
  
- file: /mnt/d/AI program/context-engineering-intro/CLAUDE.md
  why: Project guidelines including file size limits, testing requirements
  
- file: /mnt/d/AI program/context-engineering-intro/INITIAL.md
  why: Complete feature requirements and technical specifications
  
- docfile: /mnt/d/AI program/context-engineering-intro/.env.example
  why: Environment variable management pattern
```

### Current Codebase tree
```bash
.
├── examples/
├── PRPs/
│   ├── EXAMPLE_multi_agent_prp.md
│   └── templates/
│       └── prp_base.md
├── tests/
│   ├── __init__.py
│   ├── test_geocoding.py
│   ├── test_imaging.py
│   └── test_html_generator.py
├── templates/
├── CLAUDE.md
├── INITIAL.md
├── .env.example
└── README.md
```

### Desired Codebase tree with files to be added
```bash
.
├── family-trip-planner/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── database.py                # SQLAlchemy database setup
│   │   ├── config.py                  # Configuration management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── trip.py                # Trip database model
│   │   │   ├── activity.py            # Activity database model
│   │   │   ├── family_member.py       # Family member model
│   │   │   └── base.py                # Base SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── trip.py                # Trip Pydantic schemas
│   │   │   ├── activity.py            # Activity Pydantic schemas
│   │   │   └── family_member.py       # Family member schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── trip.py                # Trip CRUD endpoints
│   │   │   ├── activity.py            # Activity CRUD endpoints
│   │   │   ├── weather.py             # Weather API endpoints
│   │   │   └── geocoding.py           # Geocoding API endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── weather_service.py     # OpenWeatherMap integration
│   │   │   ├── geocoding_service.py   # Nominatim integration
│   │   │   └── trip_service.py        # Business logic
│   │   └── dependencies.py            # FastAPI dependencies
│   ├── frontend/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── main.css           # Bootstrap + custom styles
│   │   │   ├── js/
│   │   │   │   ├── main.js            # Core JavaScript
│   │   │   │   ├── map.js             # Leaflet map integration
│   │   │   │   └── weather.js         # Weather widget
│   │   │   └── images/
│   │   │       └── icons/             # Activity category icons
│   │   └── templates/
│   │       ├── base.html              # Base template
│   │       ├── index.html             # Main dashboard
│   │       ├── daily_planner.html     # Daily activity planner
│   │       └── map.html               # Map view
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_trip_routes.py        # Trip API tests
│   │   ├── test_activity_routes.py    # Activity API tests
│   │   ├── test_weather_service.py    # Weather service tests
│   │   ├── test_geocoding_service.py  # Geocoding service tests
│   │   └── conftest.py                # Test configuration
│   ├── alembic/                       # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── .env.example                   # Environment variables template
│   ├── requirements.txt               # Python dependencies
│   ├── README.md                      # Setup and usage instructions
│   └── run.py                         # Development server script
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: FastAPI + SQLite requires check_same_thread=False
# Example: SQLite needs to allow multiple threads for FastAPI
connect_args = {"check_same_thread": False}

# CRITICAL: OpenWeatherMap API requires API key from https://openweathermap.org/appid#signup
# Example: Free tier allows 60 calls/minute, 1000 calls/day

# CRITICAL: Nominatim has strict rate limiting - 1 request per second
# Example: Use geopy.geocoders.Nominatim with user_agent parameter

# CRITICAL: Leaflet.js map initialization requires proper container height
# Example: Set explicit height in CSS: #map { height: 400px; }

# CRITICAL: Bootstrap requires proper viewport meta tag for mobile responsiveness
# Example: <meta name="viewport" content="width=device-width, initial-scale=1">

# CRITICAL: FastAPI static files require proper mounting
# Example: app.mount("/static", StaticFiles(directory="static"), name="static")

# CRITICAL: Async functions required for SQLAlchemy async operations
# Example: Use async def for all database operations with await session.execute()
```

## Implementation Blueprint

### Data models and structure

```python
# models/base.py - Base SQLAlchemy model
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# models/trip.py - Trip model
from sqlalchemy import Column, Integer, String, Date, Text
from .base import Base, TimestampMixin

class Trip(Base, TimestampMixin):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    destination = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    accommodation_address = Column(Text)
    accommodation_lat = Column(Float)
    accommodation_lon = Column(Float)
    total_budget = Column(Float, default=0.0)

# schemas/trip.py - Pydantic schemas
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class TripCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    destination: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    accommodation_address: str
    total_budget: Optional[float] = Field(0.0, ge=0)

class TripResponse(TripCreate):
    id: int
    accommodation_lat: Optional[float]
    accommodation_lon: Optional[float]
    
    class Config:
        orm_mode = True
```

### List of tasks to be completed to fulfill the PRP in order

```yaml
Task 1: Project Setup and Configuration
CREATE family-trip-planner/backend/config.py:
  - PATTERN: Use pydantic-settings like examples use os.getenv
  - Load environment variables with defaults
  - Validate required API keys present

CREATE family-trip-planner/.env.example:
  - Include all required environment variables with descriptions
  - Follow pattern from existing .env.example

CREATE family-trip-planner/requirements.txt:
  - FastAPI, SQLAlchemy, Alembic, Pydantic, httpx, geopy
  - Testing: pytest, pytest-asyncio, httpx

Task 2: Database Models and Setup
CREATE family-trip-planner/backend/models/:
  - PATTERN: Follow SQLAlchemy declarative base pattern
  - Create base.py with TimestampMixin
  - Create trip.py, activity.py, family_member.py models
  - PRESERVE foreign key relationships

CREATE family-trip-planner/backend/database.py:
  - PATTERN: Follow FastAPI SQLAlchemy tutorial structure
  - SQLite setup with check_same_thread=False
  - Session dependency for dependency injection

Task 3: Pydantic Schemas
CREATE family-trip-planner/backend/schemas/:
  - PATTERN: Mirror existing model structure
  - Create request/response schemas for each model
  - Include validation with Field constraints
  - KEEP consistent naming with database models

Task 4: External API Services
CREATE family-trip-planner/backend/services/geocoding_service.py:
  - PATTERN: Follow existing test_geocoding.py error handling
  - Use geopy.geocoders.Nominatim with user_agent
  - Rate limiting: 1 request per second
  - Return lat/lon coordinates or fallback values

CREATE family-trip-planner/backend/services/weather_service.py:
  - PATTERN: Follow existing API integration patterns
  - Use httpx for async HTTP calls
  - Handle OpenWeatherMap API responses
  - Cache weather data for 10 minutes

Task 5: FastAPI Routes
CREATE family-trip-planner/backend/routes/:
  - PATTERN: Follow domain-driven FastAPI structure
  - Create CRUD endpoints for trips, activities
  - Include proper error handling and validation
  - Use dependency injection for database sessions

CREATE family-trip-planner/backend/main.py:
  - PATTERN: Follow FastAPI tutorial structure
  - Mount static files and templates
  - Include all routers with proper prefixes
  - Add CORS middleware for frontend

Task 6: Frontend Templates
CREATE family-trip-planner/frontend/templates/:
  - PATTERN: Use Bootstrap for responsive design
  - Create base.html with common elements
  - Implement Jinja2 templating for dynamic content
  - PRESERVE mobile-first responsive design

Task 7: JavaScript Frontend Logic
CREATE family-trip-planner/frontend/static/js/:
  - PATTERN: Modern JavaScript with async/await
  - Leaflet.js map integration with OpenWeatherMap
  - AJAX calls to FastAPI backend
  - Form validation and user feedback

Task 8: Testing Suite
CREATE family-trip-planner/tests/:
  - PATTERN: Follow existing test structure from tests/
  - Mock external API calls like test_geocoding.py
  - Test CRUD operations, API integrations
  - Include happy path, edge cases, error scenarios

Task 9: Database Migrations
CREATE family-trip-planner/alembic/:
  - PATTERN: Follow SQLAlchemy Alembic setup
  - Initialize migration environment
  - Create initial migration for all models
  - Include proper foreign key constraints

Task 10: Documentation and Deployment
CREATE family-trip-planner/README.md:
  - PATTERN: Follow existing documentation style
  - Include setup instructions, API key configuration
  - Usage examples and troubleshooting
  - Architecture overview
```

### Per task pseudocode as needed

```python
# Task 4: Geocoding Service
async def geocode_address(address: str) -> tuple[float, float]:
    """
    Geocode address using Nominatim API with rate limiting.
    
    Args:
        address: Address to geocode
        
    Returns:
        Tuple of (latitude, longitude) or (0.0, 0.0) if failed
    """
    # PATTERN: Rate limiting for Nominatim (1 req/sec)
    await asyncio.sleep(1)  # Simple rate limiting
    
    try:
        # PATTERN: Use geopy like test_geocoding.py
        geolocator = Nominatim(user_agent="family-trip-planner")
        location = await geolocator.geocode(address)
        
        if location:
            return location.latitude, location.longitude
        else:
            return 0.0, 0.0
            
    except Exception as e:
        # PATTERN: Log error and return fallback
        logger.error(f"Geocoding failed for {address}: {e}")
        return 0.0, 0.0

# Task 4: Weather Service
async def get_weather_forecast(lat: float, lon: float, days: int = 7) -> dict:
    """
    Get weather forecast for location using OpenWeatherMap API.
    
    Args:
        lat: Latitude
        lon: Longitude  
        days: Number of days to forecast
        
    Returns:
        Weather forecast data or empty dict if failed
    """
    # PATTERN: Use httpx like examples
    async with httpx.AsyncClient() as client:
        try:
            # GOTCHA: OpenWeatherMap API requires API key
            params = {
                "lat": lat,
                "lon": lon,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric",
                "cnt": days
            }
            
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params=params,
                timeout=10.0
            )
            
            # PATTERN: Structured error handling
            if response.status_code != 200:
                raise WeatherAPIError(f"API returned {response.status_code}")
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Weather API failed: {e}")
            return {}

# Task 7: Frontend JavaScript Map Integration
function initializeMap(accommodationLat, accommodationLon) {
    // PATTERN: Leaflet.js initialization with proper container
    const map = L.map('map').setView([accommodationLat, accommodationLon], 13);
    
    // PATTERN: OpenStreetMap tiles (free)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // PATTERN: Add accommodation marker
    L.marker([accommodationLat, accommodationLon])
        .addTo(map)
        .bindPopup('Your Accommodation')
        .openPopup();
    
    // GOTCHA: OpenWeatherMap integration requires API key
    const weatherLayer = L.OWM.clouds({
        showLegend: false,
        opacity: 0.5,
        appId: OPENWEATHER_API_KEY
    });
    
    map.addLayer(weatherLayer);
    
    return map;
}
```

### Integration Points
```yaml
DATABASE:
  - migration: "Create trips, activities, family_members tables"
  - indexes: "CREATE INDEX idx_trip_dates ON trips(start_date, end_date)"
  - foreign_keys: "activities.trip_id REFERENCES trips.id"
  
CONFIG:
  - add to: backend/config.py
  - pattern: "OPENWEATHER_API_KEY = Field(..., env='OPENWEATHER_API_KEY')"
  - pattern: "DATABASE_URL = Field('sqlite:///./trip_planner.db', env='DATABASE_URL')"
  
ROUTES:
  - add to: backend/main.py
  - pattern: "app.include_router(trip_router, prefix='/api/trips')"
  - pattern: "app.mount('/static', StaticFiles(directory='static'))"
  
TEMPLATES:
  - add to: backend/main.py
  - pattern: "templates = Jinja2Templates(directory='templates')"
  - pattern: "return templates.TemplateResponse('index.html', {...})"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check family-trip-planner/backend/ --fix  # Auto-fix style issues
mypy family-trip-planner/backend/               # Type checking
ruff check family-trip-planner/tests/ --fix    # Test code style

# Expected: No errors. If errors, READ and fix.
```

### Level 2: Unit Tests
```python
# test_geocoding_service.py
@pytest.mark.asyncio
async def test_geocode_address_success():
    """Test successful address geocoding"""
    # PATTERN: Mock external API like test_geocoding.py
    with patch('geopy.geocoders.Nominatim.geocode') as mock_geocode:
        mock_location = Mock()
        mock_location.latitude = 34.6937
        mock_location.longitude = 135.5023
        mock_geocode.return_value = mock_location
        
        lat, lon = await geocode_address("Osaka, Japan")
        
        assert lat == 34.6937
        assert lon == 135.5023

@pytest.mark.asyncio
async def test_geocode_address_failure():
    """Test geocoding failure handling"""
    with patch('geopy.geocoders.Nominatim.geocode') as mock_geocode:
        mock_geocode.side_effect = Exception("API Error")
        
        lat, lon = await geocode_address("Invalid Address")
        
        assert lat == 0.0
        assert lon == 0.0

# test_weather_service.py
@pytest.mark.asyncio
async def test_get_weather_success():
    """Test successful weather API call"""
    # PATTERN: Mock HTTP client like test_imaging.py
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"list": [{"main": {"temp": 25}}]}
        mock_get.return_value = mock_response
        
        weather = await get_weather_forecast(34.6937, 135.5023)
        
        assert weather["list"][0]["main"]["temp"] == 25

# test_trip_routes.py
@pytest.mark.asyncio
async def test_create_trip(client):
    """Test trip creation endpoint"""
    trip_data = {
        "name": "Osaka Family Trip",
        "destination": "Osaka, Japan",
        "start_date": "2025-07-27",
        "end_date": "2025-08-02",
        "accommodation_address": "大阪市浪速区幸町1丁目2-24",
        "total_budget": 5000.0
    }
    
    response = await client.post("/api/trips/", json=trip_data)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Osaka Family Trip"
```

```bash
# Run tests iteratively until passing:
pytest family-trip-planner/tests/ -v --cov=backend --cov-report=term-missing

# If failing: Debug specific test, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the application
cd family-trip-planner
uvicorn backend.main:app --reload --port 8000

# Test the main page
curl http://localhost:8000/
# Expected: HTML response with trip planning interface

# Test trip creation API
curl -X POST http://localhost:8000/api/trips/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Osaka Family Trip",
    "destination": "Osaka, Japan", 
    "start_date": "2025-07-27",
    "end_date": "2025-08-02",
    "accommodation_address": "大阪市浪速区幸町1丁目2-24",
    "total_budget": 5000.0
  }'
# Expected: {"id": 1, "name": "Osaka Family Trip", ...}

# Test weather API
curl http://localhost:8000/api/weather/34.6937/135.5023
# Expected: {"forecast": [...], "current": {...}}

# Test geocoding API  
curl http://localhost:8000/api/geocode/大阪市浪速区幸町1丁目2-24
# Expected: {"latitude": 34.6937, "longitude": 135.5023}
```

## Final Validation Checklist
- [ ] All tests pass: `pytest family-trip-planner/tests/ -v`
- [ ] No linting errors: `ruff check family-trip-planner/backend/`
- [ ] No type errors: `mypy family-trip-planner/backend/`
- [ ] Database migrations work: `alembic upgrade head`
- [ ] Weather API integration works with valid API key
- [ ] Geocoding service respects rate limits
- [ ] Map displays correctly with accommodation marker
- [ ] Mobile responsive design works on different screen sizes
- [ ] CRUD operations work for trips and activities
- [ ] Error handling graceful for API failures
- [ ] Export functionality generates printable itinerary
- [ ] Documentation includes clear setup instructions

---

## Anti-Patterns to Avoid
- ❌ Don't expose API keys in frontend JavaScript - use backend proxy
- ❌ Don't ignore rate limits for Nominatim (1 req/sec) or OpenWeatherMap
- ❌ Don't use sync functions in async FastAPI context
- ❌ Don't skip database migrations when models change
- ❌ Don't hardcode coordinates - always geocode addresses
- ❌ Don't forget check_same_thread=False for SQLite in FastAPI
- ❌ Don't skip mobile responsiveness testing
- ❌ Don't create files longer than 500 lines (per CLAUDE.md)

## Confidence Score: 8/10

High confidence due to:
- Comprehensive research on all tech stack components
- Existing codebase patterns for testing and API integration
- Clear official documentation for FastAPI + SQLAlchemy
- Proven integration libraries for maps and weather
- Well-defined MVP scope with concrete deliverables

Minor uncertainty on:
- OpenWeatherMap API quota management for family usage
- Optimal user experience flow for collaborative planning
- Performance optimization for SQLite with concurrent users