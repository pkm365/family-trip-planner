/**
 * Family Trip Planner - Map Functionality
 * 
 * Handles Leaflet map integration and location-based features.
 */

/**
 * Map utility functions for the Family Trip Planner.
 */
class MapUtils {
    constructor() {
        this.map = null;
        this.markers = new Map();
        this.markerGroups = new Map();
        this.defaultCenter = [34.6937, 135.5023]; // Osaka, Japan
        this.defaultZoom = 13;
    }

    /**
     * Initialize a Leaflet map.
     * 
     * @param {string} containerId - Map container element ID
     * @param {Object} options - Map initialization options
     * @returns {L.Map} Leaflet map instance
     */
    initializeMap(containerId, options = {}) {
        const defaultOptions = {
            center: this.defaultCenter,
            zoom: this.defaultZoom,
            zoomControl: true,
            attributionControl: true
        };

        const mapOptions = { ...defaultOptions, ...options };

        this.map = L.map(containerId).setView(mapOptions.center, mapOptions.zoom);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);

        return this.map;
    }

    /**
     * Create a custom marker icon.
     * 
     * @param {string} iconClass - CSS class for the icon
     * @param {string} color - Icon color
     * @param {number} size - Icon size
     * @returns {L.DivIcon} Custom marker icon
     */
    createCustomIcon(iconClass, color = 'primary', size = 30) {
        return L.divIcon({
            html: `<i class="${iconClass} text-${color}" style="font-size: ${size * 0.8}px;"></i>`,
            iconSize: [size, size],
            className: 'custom-div-icon',
            iconAnchor: [size / 2, size / 2],
            popupAnchor: [0, -(size / 2)]
        });
    }

    /**
     * Add a marker to the map.
     * 
     * @param {string} id - Unique marker identifier
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @param {Object} options - Marker options
     * @returns {L.Marker} Created marker
     */
    addMarker(id, lat, lng, options = {}) {
        const defaultOptions = {
            icon: this.createCustomIcon('bi bi-geo-alt-fill'),
            title: '',
            popup: null,
            group: 'default'
        };

        const markerOptions = { ...defaultOptions, ...options };
        const marker = L.marker([lat, lng], { icon: markerOptions.icon });

        if (markerOptions.title) {
            marker.bindTooltip(markerOptions.title, {
                direction: 'top',
                offset: [0, -20]
            });
        }

        if (markerOptions.popup) {
            marker.bindPopup(markerOptions.popup);
        }

        marker.addTo(this.map);

        // Store marker
        this.markers.set(id, marker);

        // Add to group
        const group = markerOptions.group;
        if (!this.markerGroups.has(group)) {
            this.markerGroups.set(group, []);
        }
        this.markerGroups.get(group).push(marker);

        return marker;
    }

    /**
     * Remove a marker from the map.
     * 
     * @param {string} id - Marker identifier
     */
    removeMarker(id) {
        const marker = this.markers.get(id);
        if (marker) {
            this.map.removeLayer(marker);
            this.markers.delete(id);

            // Remove from groups
            this.markerGroups.forEach(group => {
                const index = group.indexOf(marker);
                if (index > -1) {
                    group.splice(index, 1);
                }
            });
        }
    }

    /**
     * Clear all markers from a group.
     * 
     * @param {string} groupName - Group name
     */
    clearMarkerGroup(groupName) {
        const group = this.markerGroups.get(groupName);
        if (group) {
            group.forEach(marker => {
                this.map.removeLayer(marker);
                
                // Remove from markers map
                for (const [id, m] of this.markers.entries()) {
                    if (m === marker) {
                        this.markers.delete(id);
                        break;
                    }
                }
            });
            this.markerGroups.set(groupName, []);
        }
    }

    /**
     * Show/hide markers in a group.
     * 
     * @param {string} groupName - Group name
     * @param {boolean} visible - Whether to show or hide
     */
    toggleMarkerGroup(groupName, visible) {
        const group = this.markerGroups.get(groupName);
        if (group) {
            group.forEach(marker => {
                if (visible) {
                    marker.addTo(this.map);
                } else {
                    this.map.removeLayer(marker);
                }
            });
        }
    }

    /**
     * Fit map view to show all markers in a group.
     * 
     * @param {string} groupName - Group name
     * @param {Object} options - Fit bounds options
     */
    fitToMarkerGroup(groupName, options = {}) {
        const group = this.markerGroups.get(groupName);
        if (group && group.length > 0) {
            const featureGroup = new L.featureGroup(group);
            this.map.fitBounds(featureGroup.getBounds(), {
                padding: [20, 20],
                maxZoom: 16,
                ...options
            });
        }
    }

    /**
     * Fit map view to show all markers.
     * 
     * @param {Object} options - Fit bounds options
     */
    fitToAllMarkers(options = {}) {
        if (this.markers.size > 0) {
            const allMarkers = Array.from(this.markers.values());
            const featureGroup = new L.featureGroup(allMarkers);
            this.map.fitBounds(featureGroup.getBounds(), {
                padding: [20, 20],
                maxZoom: 16,
                ...options
            });
        }
    }

    /**
     * Center map on specific coordinates.
     * 
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @param {number} zoom - Zoom level
     */
    centerOn(lat, lng, zoom = this.defaultZoom) {
        this.map.setView([lat, lng], zoom);
    }

    /**
     * Get marker by ID.
     * 
     * @param {string} id - Marker identifier
     * @returns {L.Marker|null} Marker or null if not found
     */
    getMarker(id) {
        return this.markers.get(id) || null;
    }

    /**
     * Get all markers in a group.
     * 
     * @param {string} groupName - Group name
     * @returns {L.Marker[]} Array of markers
     */
    getMarkerGroup(groupName) {
        return this.markerGroups.get(groupName) || [];
    }

    /**
     * Add a popup to the map at specific coordinates.
     * 
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @param {string} content - Popup content
     * @param {Object} options - Popup options
     */
    showPopup(lat, lng, content, options = {}) {
        const popup = L.popup(options)
            .setLatLng([lat, lng])
            .setContent(content)
            .openOn(this.map);

        return popup;
    }

    /**
     * Calculate distance between two points.
     * 
     * @param {number} lat1 - First point latitude
     * @param {number} lng1 - First point longitude
     * @param {number} lat2 - Second point latitude
     * @param {number} lng2 - Second point longitude
     * @returns {number} Distance in meters
     */
    calculateDistance(lat1, lng1, lat2, lng2) {
        const point1 = L.latLng(lat1, lng1);
        const point2 = L.latLng(lat2, lng2);
        return point1.distanceTo(point2);
    }

    /**
     * Format distance for display.
     * 
     * @param {number} meters - Distance in meters
     * @returns {string} Formatted distance string
     */
    formatDistance(meters) {
        if (meters < 1000) {
            return `${Math.round(meters)}m`;
        } else {
            return `${(meters / 1000).toFixed(1)}km`;
        }
    }

    /**
     * Add a circle overlay to the map.
     * 
     * @param {number} lat - Center latitude
     * @param {number} lng - Center longitude
     * @param {number} radius - Radius in meters
     * @param {Object} options - Circle options
     * @returns {L.Circle} Created circle
     */
    addCircle(lat, lng, radius, options = {}) {
        const defaultOptions = {
            color: '#3388ff',
            fillColor: '#3388ff',
            fillOpacity: 0.2,
            weight: 2
        };

        const circleOptions = { ...defaultOptions, ...options };
        const circle = L.circle([lat, lng], radius, circleOptions);
        circle.addTo(this.map);

        return circle;
    }

    /**
     * Get current map bounds.
     * 
     * @returns {Object} Bounds object with north, south, east, west
     */
    getBounds() {
        const bounds = this.map.getBounds();
        return {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };
    }

    /**
     * Check if coordinates are within current map view.
     * 
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @returns {boolean} Whether coordinates are in view
     */
    isInView(lat, lng) {
        return this.map.getBounds().contains([lat, lng]);
    }

    /**
     * Destroy the map and clean up resources.
     */
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
            this.markers.clear();
            this.markerGroups.clear();
        }
    }
}

/**
 * Trip-specific map functionality.
 */
class TripMap extends MapUtils {
    constructor() {
        super();
        this.accommodationMarker = null;
        this.activityMarkers = new Map();
        this.currentTrip = null;
    }

    /**
     * Load trip data on the map.
     * 
     * @param {Object} trip - Trip data
     * @param {Array} activities - Array of activities
     */
    loadTripData(trip, activities) {
        this.currentTrip = trip;

        // Clear existing data
        this.clearTripData();

        // Add accommodation marker
        if (trip.accommodation_lat && trip.accommodation_lon) {
            this.addAccommodationMarker(trip);
        }

        // Add activity markers
        const activitiesWithCoords = activities.filter(a => a.latitude && a.longitude);
        this.addActivityMarkers(activitiesWithCoords);

        // Fit map to show all markers
        this.fitToAllMarkers();
    }

    /**
     * Add accommodation marker to the map.
     * 
     * @param {Object} trip - Trip data
     */
    addAccommodationMarker(trip) {
        const icon = this.createCustomIcon('bi bi-house-fill', 'primary', 35);
        
        const popupContent = `
            <div class="popup-content">
                <h6><i class="bi bi-house"></i> Accommodation</h6>
                <p class="mb-1"><strong>${trip.name}</strong></p>
                <p class="mb-0">${trip.accommodation_address}</p>
            </div>
        `;

        this.accommodationMarker = this.addMarker(
            'accommodation',
            trip.accommodation_lat,
            trip.accommodation_lon,
            {
                icon: icon,
                title: 'Accommodation',
                popup: popupContent,
                group: 'accommodation'
            }
        );
    }

    /**
     * Add activity markers to the map.
     * 
     * @param {Array} activities - Array of activities with coordinates
     */
    addActivityMarkers(activities) {
        activities.forEach(activity => {
            const icon = this.getActivityIcon(activity.category);
            
            const popupContent = this.createActivityPopup(activity);

            const marker = this.addMarker(
                `activity-${activity.id}`,
                activity.latitude,
                activity.longitude,
                {
                    icon: icon,
                    title: activity.name,
                    popup: popupContent,
                    group: 'activities'
                }
            );

            this.activityMarkers.set(activity.id, marker);

            // Add click handler for activity highlighting
            marker.on('click', () => {
                this.highlightActivity(activity.id);
            });
        });
    }

    /**
     * Get appropriate icon for activity category.
     * 
     * @param {string} category - Activity category
     * @returns {L.DivIcon} Activity icon
     */
    getActivityIcon(category) {
        const iconMap = {
            sightseeing: { icon: 'bi bi-camera-fill', color: 'success' },
            food: { icon: 'bi bi-cup-hot-fill', color: 'warning' },
            shopping: { icon: 'bi bi-bag-fill', color: 'info' },
            rest: { icon: 'bi bi-house-fill', color: 'primary' },
            transportation: { icon: 'bi bi-train-front-fill', color: 'secondary' }
        };

        const config = iconMap[category] || { icon: 'bi bi-geo-alt-fill', color: 'secondary' };
        return this.createCustomIcon(config.icon, config.color, 30);
    }

    /**
     * Create popup content for activity.
     * 
     * @param {Object} activity - Activity data
     * @returns {string} HTML popup content
     */
    createActivityPopup(activity) {
        const categoryColors = {
            sightseeing: 'success',
            food: 'warning',
            shopping: 'info',
            rest: 'primary',
            transportation: 'secondary'
        };

        const priorityColors = {
            must_do: 'danger',
            would_like: 'primary',
            optional: 'secondary'
        };

        const categoryColor = categoryColors[activity.category] || 'secondary';
        const priorityColor = priorityColors[activity.priority] || 'secondary';

        return `
            <div class="popup-content">
                <h6><i class="bi bi-${this.getActivityIconName(activity.category)}"></i> ${activity.name}</h6>
                <p class="mb-1">
                    <span class="badge bg-${categoryColor}">${activity.category}</span>
                    <span class="badge bg-${priorityColor} ms-1">${activity.priority.replace('_', ' ')}</span>
                </p>
                <p class="mb-1"><strong>Date:</strong> ${formatDate(activity.activity_date)}</p>
                <p class="mb-1"><strong>Time:</strong> ${activity.time_slot}</p>
                ${activity.location_name ? `<p class="mb-1"><strong>Location:</strong> ${activity.location_name}</p>` : ''}
                ${activity.estimated_cost > 0 ? `<p class="mb-1"><strong>Cost:</strong> $${activity.estimated_cost}</p>` : ''}
                ${activity.description ? `<p class="mb-0">${activity.description}</p>` : ''}
            </div>
        `;
    }

    /**
     * Get icon name for activity category.
     * 
     * @param {string} category - Activity category
     * @returns {string} Icon name
     */
    getActivityIconName(category) {
        const icons = {
            sightseeing: 'camera-fill',
            food: 'cup-hot-fill',
            shopping: 'bag-fill',
            rest: 'house-fill',
            transportation: 'train-front-fill'
        };
        return icons[category] || 'geo-alt-fill';
    }

    /**
     * Highlight specific activity on map and in UI.
     * 
     * @param {number} activityId - Activity ID
     */
    highlightActivity(activityId) {
        // Trigger custom event for UI highlighting
        document.dispatchEvent(new CustomEvent('activityHighlight', {
            detail: { activityId }
        }));
    }

    /**
     * Center map on specific activity.
     * 
     * @param {number} activityId - Activity ID
     */
    centerOnActivity(activityId) {
        const marker = this.activityMarkers.get(activityId);
        if (marker) {
            const latlng = marker.getLatLng();
            this.centerOn(latlng.lat, latlng.lng, 16);
            marker.openPopup();
        }
    }

    /**
     * Clear all trip-related data from the map.
     */
    clearTripData() {
        // Clear accommodation
        if (this.accommodationMarker) {
            this.removeMarker('accommodation');
            this.accommodationMarker = null;
        }

        // Clear activities
        this.clearMarkerGroup('activities');
        this.activityMarkers.clear();

        this.currentTrip = null;
    }

    /**
     * Calculate total trip distance (accommodation to all activities).
     * 
     * @returns {number} Total distance in meters
     */
    calculateTripDistance() {
        if (!this.accommodationMarker || this.activityMarkers.size === 0) {
            return 0;
        }

        const accommodationLatLng = this.accommodationMarker.getLatLng();
        let totalDistance = 0;

        this.activityMarkers.forEach(marker => {
            const activityLatLng = marker.getLatLng();
            totalDistance += this.calculateDistance(
                accommodationLatLng.lat,
                accommodationLatLng.lng,
                activityLatLng.lat,
                activityLatLng.lng
            );
        });

        return totalDistance;
    }
}

// Global instance for use across pages
let tripMap = null;

// Initialize map utilities when needed
function initializeTripMap(containerId, options = {}) {
    tripMap = new TripMap();
    return tripMap.initializeMap(containerId, options);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        MapUtils,
        TripMap,
        initializeTripMap
    };
}