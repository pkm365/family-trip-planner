# API Documentation - Family Trip Planner

## 📋 Overview

This document describes the enhanced API endpoints and their usage patterns for the Family Trip Planner application.

## 🔗 Base URL
```
http://127.0.0.1:8000
```

## 🗂️ API Endpoints

### 🎯 Trips Management

#### Get All Trips
```http
GET /api/trips/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Osaka Family Trip",
    "destination": "Osaka, Japan", 
    "start_date": "2025-07-27",
    "end_date": "2025-08-02",
    "accommodation_address": "大阪市浪速区幸町1丁目2-24",
    "accommodation_lat": 34.6937,
    "accommodation_lon": 135.5023,
    "total_budget": 5000.0,
    "created_at": "2025-07-05T13:51:38",
    "updated_at": "2025-07-05T13:51:38"
  }
]
```

#### Get Trip Details
```http
GET /api/trips/{trip_id}
```

#### Create New Trip
```http
POST /api/trips/
Content-Type: application/json

{
  "name": "Tokyo Adventure",
  "destination": "Tokyo, Japan",
  "start_date": "2025-08-15",
  "end_date": "2025-08-22", 
  "accommodation_address": "東京都新宿区...",
  "total_budget": 6000.0
}
```

#### Update Trip
```http
PUT /api/trips/{trip_id}
Content-Type: application/json

{
  "name": "Updated Trip Name",
  "total_budget": 5500.0
}
```

#### Delete Trip
```http
DELETE /api/trips/{trip_id}
```

#### Get Daily Activities (NEW)
```http
GET /api/trips/{trip_id}/daily-activities
```

**Response:**
```json
[
  {
    "date": "2025-07-27",
    "morning": [
      {
        "id": 1,
        "name": "Visit Osaka Castle",
        "category": "sightseeing",
        "priority": "must_do",
        "estimated_cost": 600.0,
        "activity_date": "2025-07-27",
        "time_slot": "morning"
      }
    ],
    "afternoon": [],
    "evening": [
      {
        "id": 2,
        "name": "Dotonbori Food Tour", 
        "category": "food",
        "priority": "must_do",
        "estimated_cost": 3000.0,
        "activity_date": "2025-07-27",
        "time_slot": "evening"
      }
    ],
    "total_estimated_cost": 3600.0
  }
]
```

### 🎨 Activities Management

#### Get All Activities
```http
GET /api/activities/
```

**Query Parameters:**
- `trip_id` (int): Filter by trip ID
- `activity_date` (date): Filter by date
- `time_slot` (enum): morning|afternoon|evening
- `category` (enum): sightseeing|food|shopping|rest|transportation
- `priority` (enum): must_do|would_like|optional
- `skip` (int): Pagination offset
- `limit` (int): Items per page

**Example:**
```http
GET /api/activities/?trip_id=1&time_slot=morning&limit=5
```

#### Get Activity Details
```http
GET /api/activities/{activity_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Visit Osaka Castle",
  "description": "Explore the historic Osaka Castle and gardens",
  "trip_id": 1,
  "activity_date": "2025-07-27", 
  "time_slot": "afternoon",
  "category": "sightseeing",
  "priority": "must_do",
  "location_name": "Osaka Castle",
  "address": "1-1 Osakajo, Chuo Ward, Osaka",
  "latitude": 34.6873,
  "longitude": 135.5262,
  "estimated_cost": 600.0,
  "actual_cost": null,
  "notes": "Book tickets in advance",
  "created_at": "2025-07-05T13:51:38",
  "updated_at": "2025-07-05T13:51:38"
}
```

#### Create New Activity
```http
POST /api/activities/
Content-Type: application/json

{
  "trip_id": 1,
  "name": "Visit Fushimi Inari Shrine",
  "description": "Explore the famous torii gates",
  "activity_date": "2025-07-28",
  "time_slot": "morning",
  "category": "sightseeing", 
  "priority": "would_like",
  "location_name": "Fushimi Inari Taisha",
  "address": "68 Fukakusa Yabunouchicho, Fushimi Ward, Kyoto",
  "estimated_cost": 0.0,
  "notes": "Free admission, wear comfortable shoes"
}
```

#### Update Activity (ENHANCED)
```http
PUT /api/activities/{activity_id}
Content-Type: application/json

{
  "name": "Updated Activity Name",
  "activity_date": "2025-07-29",
  "time_slot": "evening",
  "estimated_cost": 800.0
}
```

**Key Features:**
- ✅ **Partial Updates**: Only send fields you want to change
- ✅ **Automatic Geocoding**: Re-geocodes if address is updated
- ✅ **Drag-Drop Support**: Can update just `activity_date` and `time_slot`
- ✅ **Validation**: Server-side validation for all fields

#### Delete Activity
```http
DELETE /api/activities/{activity_id}
```

### 👨‍👩‍👧‍👦 Family Members Management

#### Get Family Members
```http
GET /api/family-members/
```

**Query Parameters:**
- `trip_id` (int): Filter by trip ID
- `role` (enum): parent|child|adult

**Example:**
```http
GET /api/family-members/?trip_id=1
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "冯可嘉",
    "role": "parent",
    "age": 45
  },
  {
    "id": 2, 
    "name": "纪雪萍",
    "role": "parent",
    "age": 42
  },
  {
    "id": 3,
    "name": "冯欣瑜", 
    "role": "child",
    "age": 16
  }
]
```

#### Get Family Member Details
```http
GET /api/family-members/{member_id}
```

#### Create Family Member
```http
POST /api/family-members/
Content-Type: application/json

{
  "trip_id": 1,
  "name": "张小明",
  "role": "child", 
  "age": 10,
  "dietary_restrictions": "Vegetarian",
  "interests": "Animals, Games",
  "notes": "Loves theme parks"
}
```

#### Update Family Member
```http
PUT /api/family-members/{member_id}
Content-Type: application/json

{
  "age": 11,
  "interests": "Animals, Games, Reading"
}
```

#### Delete Family Member
```http
DELETE /api/family-members/{member_id}
```

### 🌤️ Weather Integration

#### Get Trip Weather
```http
GET /api/trips/{trip_id}/weather
```

#### Get Current Weather
```http
GET /api/weather/current/{lat}/{lon}
```

#### Get Weather Forecast
```http
GET /api/weather/forecast/{lat}/{lon}
```

### 🗺️ Geocoding Services

#### Geocode Address
```http
GET /api/geocoding/geocode?address={address}
```

#### Reverse Geocode
```http
GET /api/geocoding/reverse-geocode?lat={lat}&lon={lon}
```

#### Batch Geocoding
```http
POST /api/geocoding/batch-geocode
Content-Type: application/json

{
  "addresses": ["Address 1", "Address 2", "Address 3"]
}
```

## 📝 Data Models

### Activity Model
```json
{
  "id": "integer",
  "name": "string (max 200 chars)",
  "description": "string (optional)",
  "trip_id": "integer (foreign key)",
  "activity_date": "date (YYYY-MM-DD)",
  "time_slot": "enum (morning|afternoon|evening)",
  "category": "enum (sightseeing|food|shopping|rest|transportation)",
  "priority": "enum (must_do|would_like|optional)",
  "location_name": "string (optional, max 200 chars)",
  "address": "string (optional)",
  "latitude": "float (optional, -90 to 90)",
  "longitude": "float (optional, -180 to 180)",
  "estimated_cost": "float (default 0.0)",
  "actual_cost": "float (optional)",
  "notes": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Family Member Model
```json
{
  "id": "integer",
  "name": "string (max 100 chars)",
  "role": "enum (parent|child|adult)",
  "age": "integer (optional, 0-120)",
  "trip_id": "integer (foreign key)",
  "dietary_restrictions": "string (optional)",
  "mobility_needs": "string (optional)",
  "interests": "string (optional)",
  "wishlist_items": "string (optional)",
  "notes": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## ⚠️ Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content (for DELETE)
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Examples

**Validation Error (400):**
```json
{
  "detail": "activity_date: field required"
}
```

**Not Found (404):**
```json
{
  "detail": "Activity with id 999 not found"
}
```

**Server Error (500):**
```json
{
  "detail": "Error updating activity: Invalid time slot"
}
```

## 🔄 API Usage Patterns

### Drag-and-Drop Activity Update
```javascript
// Frontend drag-drop implementation
async function moveActivity(activityId, newDate, newTimeSlot) {
  try {
    const response = await fetch(`/api/activities/${activityId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        activity_date: newDate,
        time_slot: newTimeSlot
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const updatedActivity = await response.json();
    return updatedActivity;
  } catch (error) {
    console.error('Move failed:', error);
    throw error;
  }
}
```

### Loading Dashboard Statistics
```javascript
// Get real-time counts for dashboard
async function loadDashboardStats() {
  const trips = await fetch('/api/trips/').then(r => r.json());
  
  let totalActivities = 0;
  let totalMembers = 0;
  
  for (const trip of trips) {
    // Get activities count
    const activities = await fetch(`/api/activities/?trip_id=${trip.id}`)
      .then(r => r.json());
    totalActivities += activities.length;
    
    // Get family members count  
    const members = await fetch(`/api/family-members/?trip_id=${trip.id}`)
      .then(r => r.json());
    totalMembers += members.length;
  }
  
  return { totalActivities, totalMembers, totalTrips: trips.length };
}
```

### Daily Activities Organization
```javascript
// Load organized daily activities
async function loadDailyActivities(tripId) {
  const response = await fetch(`/api/trips/${tripId}/daily-activities`);
  const dailyData = await response.json();
  
  // Data is pre-organized by date and time slot
  dailyData.forEach(day => {
    console.log(`${day.date}: ${day.morning.length + day.afternoon.length + day.evening.length} activities`);
    console.log(`Total cost: $${day.total_estimated_cost}`);
  });
  
  return dailyData;
}
```

## 🧪 Testing with curl

### Create Activity
```bash
curl -X POST "http://127.0.0.1:8000/api/activities/" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": 1,
    "name": "Test Activity",
    "activity_date": "2025-07-27", 
    "time_slot": "morning",
    "category": "sightseeing",
    "priority": "would_like"
  }'
```

### Update Activity (Drag-Drop Simulation)
```bash
curl -X PUT "http://127.0.0.1:8000/api/activities/1" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_date": "2025-07-28",
    "time_slot": "evening"
  }'
```

### Get Daily Activities
```bash
curl "http://127.0.0.1:8000/api/trips/1/daily-activities"
```

---

## 📚 Interactive API Documentation

When the server is running, you can access interactive API documentation at:
- **Swagger UI**: http://127.0.0.1:8000/api/docs
- **ReDoc**: http://127.0.0.1:8000/api/redoc

These provide live testing capabilities and detailed schema information.