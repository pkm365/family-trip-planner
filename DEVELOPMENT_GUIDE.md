# Development Guide - Family Trip Planner

## 🏗️ Architecture Overview

### Frontend Architecture
```
frontend/
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base template with nav + i18n
│   ├── index.html      # Dashboard with real-time stats
│   └── daily_planner.html # Enhanced planning with drag-drop
├── static/
│   ├── js/
│   │   ├── main.js     # Core utilities and API functions
│   │   └── i18n.js     # Internationalization system
│   └── css/
│       └── main.css    # Enhanced with drag-drop styles
```

### Backend Architecture
```
backend/
├── models/             # SQLAlchemy database models
├── schemas/            # Pydantic validation schemas  
├── routes/             # FastAPI route handlers
├── services/           # Business logic layer
├── config.py          # Configuration management
├── database.py        # Database session management
└── main.py            # FastAPI application entry
```

## 🔧 Key Components Deep Dive

### 1. Internationalization System (`i18n.js`)

**Core Functions:**
```javascript
setCurrentLanguage(lang)    // Switch language + persist
t(key, lang)               // Get translation for key
updateTranslations()       // Update all DOM elements
initializeLanguageSelector() // Setup navigation dropdown
```

**Usage Pattern:**
```html
<!-- HTML template -->
<span data-i18n="activity.name">Activity Name</span>

<!-- JavaScript -->
const text = t('activity.name'); // Returns translated text
```

**Adding New Languages:**
```javascript
// 1. Add to LANGUAGES object
const LANGUAGES = {
  en: { name: 'English', flag: '🇺🇸', code: 'en' },
  zh: { name: '中文', flag: '🇨🇳', code: 'zh' },
  ja: { name: '日本語', flag: '🇯🇵', code: 'ja' } // NEW
};

// 2. Add translations
TRANSLATIONS.ja = {
  'nav.dashboard': 'ダッシュボード',
  // ... add all keys
};
```

### 2. Drag-and-Drop System

**HTML Structure:**
```html
<!-- Draggable activity card -->
<div class="activity-card" 
     draggable="true" 
     data-activity-id="${id}"
     data-activity-date="${date}"
     data-activity-timeslot="${slot}"
     ondragstart="handleDragStart(event)">
  <!-- Card content -->
</div>

<!-- Drop zone -->
<div class="drop-zone" 
     data-date="${date}" 
     data-timeslot="${slot}"
     ondragover="handleDragOver(event)"
     ondrop="handleDrop(event)">
  <!-- Activities render here -->
</div>
```

**Event Flow:**
1. `handleDragStart()` - Store activity data, add visual effects
2. `handleDragEnter()` - Highlight drop zones
3. `handleDragOver()` - Allow drop operation
4. `handleDrop()` - Update activity via API call
5. `handleDragEnd()` - Clean up visual effects

**CSS Classes:**
```css
.activity-card.dragging     # Applied during drag
.drop-zone.drag-over       # Applied when hovering over drop zone
.drag-handle               # Grip icon for dragging
```

### 3. Enhanced API Endpoints

**New Daily Activities Endpoint:**
```python
@router.get("/{trip_id}/daily-activities")
def get_trip_daily_activities(trip_id: int, db: DatabaseSession):
    # Returns activities organized by date and time slot
    return [
        {
            'date': '2025-07-27',
            'morning': [activity_objects],
            'afternoon': [activity_objects], 
            'evening': [activity_objects],
            'total_estimated_cost': 1500.0
        }
    ]
```

**Activity Update Pattern:**
```python
@router.put("/{activity_id}")
async def update_activity(activity_id: int, data: ActivityUpdate, db: DatabaseSession):
    # Partial updates supported
    # Automatically re-geocodes if address changed
```

## 🛠️ Common Development Tasks

### Adding New Activity Fields

**1. Update Database Model:**
```python
# backend/models/activity.py
class Activity(BaseModel):
    # ... existing fields
    new_field = Column(String(100), nullable=True)
```

**2. Update Schemas:**
```python
# backend/schemas/activity.py  
class ActivityBase(BaseModel):
    # ... existing fields
    new_field: Optional[str] = Field(None, description="New field")
```

**3. Add to Forms:**
```html
<!-- frontend/templates/daily_planner.html -->
<div class="mb-3">
    <label for="newField" class="form-label" data-i18n="activity.new_field">New Field</label>
    <input type="text" class="form-control" id="newField">
</div>
```

**4. Add Translation Keys:**
```javascript
// frontend/static/js/i18n.js
TRANSLATIONS.en['activity.new_field'] = 'New Field';
TRANSLATIONS.zh['activity.new_field'] = '新字段';
```

**5. Update JavaScript:**
```javascript
// In createActivity() and updateActivity() functions
const activityData = {
    // ... existing fields
    new_field: document.getElementById('newField').value
};
```

### Adding New Language Support

**1. Language Configuration:**
```javascript
// Add to LANGUAGES object
fr: { name: 'Français', flag: '🇫🇷', code: 'fr' }
```

**2. Translation Object:**
```javascript
TRANSLATIONS.fr = {
    // Copy all keys from English and translate
    'nav.dashboard': 'Tableau de bord',
    'activity.add_activity': 'Ajouter une activité',
    // ... all other keys
};
```

**3. Locale-specific Formatting:**
```javascript
// Update formatDate() and formatCurrency() functions
function formatDate(dateString, locale = getCurrentLanguage()) {
    const date = new Date(dateString);
    const localeMap = { en: 'en-US', zh: 'zh-CN', fr: 'fr-FR' };
    return date.toLocaleDateString(localeMap[locale] || 'en-US');
}
```

### Extending Drag-and-Drop

**1. New Draggable Elements:**
```html
<div class="draggable-item" 
     draggable="true"
     data-item-type="new_type"
     data-item-id="${id}"
     ondragstart="handleNewDragStart(event)">
```

**2. New Drop Zones:**
```html
<div class="drop-zone new-drop-zone" 
     data-drop-type="new_target"
     ondrop="handleNewDrop(event)">
```

**3. Custom Drag Handlers:**
```javascript
function handleNewDragStart(event) {
    // Store drag data
    draggedItem = {
        type: event.target.getAttribute('data-item-type'),
        id: event.target.getAttribute('data-item-id')
    };
    
    // Visual feedback
    event.target.classList.add('dragging');
}
```

## 📊 Data Flow Patterns

### Activity Management Flow
```
User Action → Frontend Validation → API Call → Database Update → UI Refresh
     ↓              ↓                  ↓            ↓             ↓
Click Edit → Form Validation → PUT /api/activities/{id} → Update DB → Reload View
Drag Drop  → Position Check  → PUT /api/activities/{id} → Update DB → Optimistic UI
```

### Language Switching Flow
```
User Selection → Set Language → Update localStorage → Update DOM → Trigger Event
      ↓              ↓               ↓                ↓            ↓
Click Flag → setCurrentLanguage() → Save Preference → updateTranslations() → languageChanged Event
```

### Dashboard Statistics Flow
```
Page Load → Load Trips → For Each Trip → Get Activities & Members → Update Counters
    ↓          ↓             ↓                ↓                      ↓
loadDashboard → API call → Loop trips → Parallel API calls → updateStats()
```

## 🧪 Testing Strategies

### Manual Testing Checklist

**Language Support:**
- [ ] Switch languages in navigation
- [ ] Check all modals translate correctly
- [ ] Verify language persists on page reload
- [ ] Test dropdown options translate

**Drag-and-Drop:**
- [ ] Drag activities between time slots
- [ ] Drag activities between different dates  
- [ ] Verify visual feedback during drag
- [ ] Test mobile touch drag (if supported)
- [ ] Check error handling for failed moves

**Activity Management:**
- [ ] Create new activities with all fields
- [ ] Edit existing activities and save changes
- [ ] Delete activities and verify removal
- [ ] Test form validation and error messages

### Automated Testing Ideas

**Unit Tests:**
```javascript
// Test translation system
describe('i18n System', () => {
    test('should return correct translation', () => {
        setCurrentLanguage('zh');
        expect(t('nav.dashboard')).toBe('仪表板');
    });
});

// Test drag-drop utilities
describe('Drag Drop', () => {
    test('should extract activity data correctly', () => {
        const mockEvent = { target: { getAttribute: (attr) => 'test-value' } };
        const data = extractActivityData(mockEvent);
        expect(data.id).toBe('test-value');
    });
});
```

**Integration Tests:**
```python
# Test API endpoints
def test_daily_activities_endpoint():
    response = client.get("/api/trips/1/daily-activities")
    assert response.status_code == 200
    assert "morning" in response.json()[0]

def test_activity_update():
    response = client.put("/api/activities/1", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
```

## 🚀 Performance Considerations

### Frontend Optimization
- **Debounce API calls** during rapid drag operations
- **Batch DOM updates** when switching languages
- **Lazy load** large activity lists
- **Cache translations** to avoid repeated lookups

### Backend Optimization
- **Database indexing** on frequently queried fields (trip_id, activity_date)
- **Query optimization** for daily activities endpoint
- **Response caching** for translation data
- **Async operations** for non-critical updates

### Memory Management
- **Clean up event listeners** when components unmount
- **Remove DOM references** in drag-drop handlers
- **Limit concurrent API calls** to prevent browser throttling

## 🔐 Security Best Practices

### Input Validation
- **Sanitize all user input** before database operations
- **Validate drag-drop operations** server-side
- **Check user permissions** for activity modifications
- **Escape HTML content** in translations

### API Security  
- **Rate limiting** on update endpoints
- **Request validation** using Pydantic schemas
- **Error message sanitization** to prevent information leakage
- **CORS configuration** for production deployment

---

This guide should be updated whenever significant architectural changes are made to the system.