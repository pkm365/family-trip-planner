# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Development Commands

### Virtual Environment & Setup
```bash
# Use the Unix virtual environment for all Python commands
source venv_linux/bin/activate
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server (with hot reload)
venv_linux/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Alternative using run.py
venv_linux/bin/python run.py
```

### Database Management
```bash
# Run database migrations
venv_linux/bin/python -m alembic upgrade head

# Create new migration
venv_linux/bin/python -m alembic revision --autogenerate -m "description"
```

### Testing
```bash
# Run all tests
venv_linux/bin/python -m pytest

# Run specific test file
venv_linux/bin/python -m pytest tests/test_activity_routes.py

# Run with coverage
venv_linux/bin/python -m pytest --cov=backend tests/
```

### Code Quality
```bash
# Linting and formatting
venv_linux/bin/python -m ruff check .
venv_linux/bin/python -m ruff format .

# Type checking
venv_linux/bin/python -m mypy backend/
```

## 🏗️ Architecture Overview

### Backend Structure (FastAPI)
```
backend/
├── main.py              # Application entry point, CORS, route registration
├── config.py            # Pydantic settings with environment variables
├── database.py          # SQLAlchemy engine, session management
├── dependencies.py      # FastAPI dependency injection (get_db)
├── models/             # SQLAlchemy ORM models
│   ├── trip.py         # Core Trip model with relationships
│   ├── activity.py     # Activity model with scheduling/categorization
│   ├── family_member.py # Family member roles and preferences
│   └── base.py         # Base model with timestamps
├── schemas/            # Pydantic validation schemas (API contracts)
├── routes/             # API endpoint handlers grouped by feature
│   ├── trip.py         # CRUD + weather integration
│   ├── activity.py     # CRUD + daily organization + filtering
│   ├── family_member.py # Member management
│   ├── weather.py      # OpenWeatherMap integration
│   └── geocoding.py    # Address geocoding service
└── services/           # Business logic and external API integrations
    ├── weather_service.py    # Weather API with caching
    ├── geocoding_service.py  # Address resolution
    └── trip_service.py       # Trip-specific business logic
```

### Frontend Structure (Jinja2 + Vanilla JS)
```
frontend/
├── templates/          # Server-side rendered templates
│   ├── base.html       # Base template with navigation
│   ├── daily_planner.html # Main drag-and-drop planning interface
│   ├── discovery_hub.html # Activity discovery and search
│   └── map.html        # Leaflet.js map integration
└── static/
    ├── css/main.css    # Bootstrap 5 + custom drag-drop styles
    └── js/
        ├── main.js     # API utilities and DOM helpers
        ├── i18n.js     # English/Chinese internationalization
        ├── map.js      # Leaflet map with activity markers
        └── weather.js  # Weather display components
```

### Database Models & Relationships
- **Trip**: Core entity with destination, dates, budget, accommodation coordinates
- **Activity**: Rich scheduling with time_slot (morning/afternoon/evening), category, priority levels
- **FamilyMember**: Roles (parent/child/adult) with preferences and collaboration features
- **ActivityRecommendation, ActivityVote, ActivityFavorite**: Extended collaborative features

### Key Features
1. **Drag-and-drop daily planning** with time slot organization
2. **Internationalization** (English/Chinese) with browser detection
3. **Weather integration** for trip destinations with forecasts
4. **Interactive maps** with Leaflet.js and activity locations
5. **Collaborative planning** with voting and favorites
6. **External API integration**: OpenWeatherMap, Google Places

## 🛠️ Development Patterns

### API Design
- **REST conventions** with comprehensive filtering (date, category, priority, time_slot)
- **Pydantic schemas** for request/response validation
- **FastAPI dependency injection** for database sessions
- **Error handling** with proper HTTP status codes

### Database Patterns
- **SQLAlchemy ORM** with relationship management
- **Alembic migrations** for schema changes
- **Base model** with automatic timestamps
- **Enum support** for categories, priorities, time slots

### Frontend Patterns
- **Template inheritance** with Jinja2 base template
- **API integration** via fetch() with error handling
- **Event-driven** drag-and-drop with visual feedback
- **Responsive design** with Bootstrap 5 grid system

### Testing Approach
- **Pytest fixtures** for database setup and cleanup
- **Mocked external APIs** (weather, geocoding)
- **Integration tests** for API endpoints
- **Test database isolation** with SQLite

## 🔧 Configuration

### Environment Variables (Required)
```env
DATABASE_URL=sqlite:///./trip_planner.db
OPENWEATHER_API_KEY=your_api_key
GOOGLE_PLACES_API_KEY=your_api_key
DEBUG=True
```

### Development Setup
1. Database auto-creates tables on startup
2. Sample data seeding in debug mode (Osaka trip example)
3. Hot reload enabled for backend changes
4. CORS configured for local development

## 📊 Application Flow

### Daily Planning Workflow
1. **Trip creation** with destination and date range
2. **Family member addition** with preferences
3. **Activity planning** via drag-and-drop interface organized by date/time
4. **Weather checking** for trip dates
5. **Map visualization** of activity locations
6. **Collaborative features** for voting and favorites

### Data Processing
- **Geocoding**: Automatic coordinate resolution for addresses
- **Weather**: Real-time API calls with caching for performance
- **Time slots**: Morning/afternoon/evening organization for activities
- **Cost tracking**: Budget management across activities and trips

## ⚠️ Important Notes

### Virtual Environment
- **Always use `venv_linux/bin/python`** for all Python commands
- **Never use system Python** or Windows venv paths

### Database Considerations
- **SQLite for development** with potential PostgreSQL migration for production
- **Migration files** are version controlled in `alembic/versions/`
- **Sample data** automatically loads in debug mode

### External Dependencies
- **API keys required** for weather and geocoding features
- **Internet connection needed** for external API integrations
- **Leaflet.js and Bootstrap** loaded via CDN

### Code Quality Standards
- **Type hints required** for all functions
- **Docstrings mandatory** for public functions using Google style
- **Error handling** with proper logging and user feedback
- **Test coverage** expected for new features and API endpoints