/**
 * Family Trip Planner - Weather Functionality
 * 
 * Handles weather data display and integration.
 */

/**
 * Weather utility functions for the Family Trip Planner.
 */
class WeatherUtils {
    constructor() {
        this.weatherCache = new Map();
        this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
    }

    /**
     * Get weather data for coordinates.
     * 
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {boolean} useCache - Whether to use cached data
     * @returns {Promise<Object>} Weather data
     */
    async getWeatherData(lat, lon, useCache = true) {
        const cacheKey = `${lat},${lon}`;
        
        // Check cache first
        if (useCache && this.weatherCache.has(cacheKey)) {
            const cached = this.weatherCache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            const data = await apiRequest(`/api/weather/combined/${lat}/${lon}`);
            
            // Cache the result
            this.weatherCache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });

            return data;
        } catch (error) {
            console.error('Error fetching weather data:', error);
            return null;
        }
    }

    /**
     * Get current weather for coordinates.
     * 
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @returns {Promise<Object>} Current weather data
     */
    async getCurrentWeather(lat, lon) {
        try {
            return await apiRequest(`/api/weather/current/${lat}/${lon}`);
        } catch (error) {
            console.error('Error fetching current weather:', error);
            return null;
        }
    }

    /**
     * Get weather forecast for coordinates.
     * 
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number} days - Number of days to forecast
     * @returns {Promise<Object>} Weather forecast data
     */
    async getWeatherForecast(lat, lon, days = 5) {
        try {
            return await apiRequest(`/api/weather/forecast/${lat}/${lon}?days=${days}`);
        } catch (error) {
            console.error('Error fetching weather forecast:', error);
            return null;
        }
    }

    /**
     * Create weather widget HTML.
     * 
     * @param {Object} weatherData - Weather data
     * @param {Object} options - Widget options
     * @returns {string} HTML for weather widget
     */
    createWeatherWidget(weatherData, options = {}) {
        const defaultOptions = {
            showForecast: true,
            showDetails: true,
            compact: false,
            theme: 'light'
        };

        const widgetOptions = { ...defaultOptions, ...options };

        if (!weatherData || !weatherData.current) {
            return this.createErrorWidget('Weather data unavailable');
        }

        const current = weatherData.current;
        const forecast = weatherData.daily_forecasts || [];

        let html = `
            <div class="weather-widget ${widgetOptions.theme === 'dark' ? 'bg-dark text-white' : 'bg-light'}">
                ${this.createCurrentWeatherSection(current, widgetOptions)}
                ${widgetOptions.showForecast && forecast.length > 0 ? 
                    this.createForecastSection(forecast, widgetOptions) : ''}
            </div>
        `;

        return html;
    }

    /**
     * Create current weather section.
     * 
     * @param {Object} current - Current weather data
     * @param {Object} options - Widget options
     * @returns {string} HTML for current weather section
     */
    createCurrentWeatherSection(current, options) {
        const temp = Math.round(current.temperature || 0);
        const feelsLike = Math.round(current.feels_like || 0);
        const description = current.description || 'Unknown';
        const humidity = current.humidity || 0;
        const iconClass = this.getWeatherIcon(current.condition || 'clear');

        if (options.compact) {
            return `
                <div class="d-flex align-items-center">
                    <i class="${iconClass} weather-icon me-2"></i>
                    <div>
                        <h5 class="mb-0">${temp}°C</h5>
                        <small class="text-muted">${description}</small>
                    </div>
                </div>
            `;
        }

        return `
            <div class="current-weather p-3">
                <div class="row align-items-center">
                    <div class="col-auto">
                        <i class="${iconClass} weather-icon"></i>
                    </div>
                    <div class="col">
                        <h3 class="mb-0">${temp}°C</h3>
                        <p class="mb-1">${description}</p>
                        ${options.showDetails ? `
                            <small class="text-muted">
                                Feels like ${feelsLike}°C • Humidity ${humidity}%
                            </small>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create forecast section.
     * 
     * @param {Array} forecast - Forecast data array
     * @param {Object} options - Widget options
     * @returns {string} HTML for forecast section
     */
    createForecastSection(forecast, options) {
        const limitedForecast = forecast.slice(0, options.compact ? 3 : 5);

        const forecastItems = limitedForecast.map(day => {
            const date = new Date(day.date);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            const iconClass = this.getWeatherIcon(day.condition || 'clear');

            return `
                <div class="forecast-item text-center ${options.compact ? 'px-2' : 'px-3'} py-2">
                    <div class="small text-muted">${dayName}</div>
                    <i class="${iconClass} my-1" style="font-size: 1.2rem;"></i>
                    <div class="small">
                        <span class="fw-bold">${Math.round(day.max_temp || 0)}°</span>
                        <span class="text-muted">${Math.round(day.min_temp || 0)}°</span>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="weather-forecast border-top">
                <div class="d-flex justify-content-between">
                    ${forecastItems}
                </div>
            </div>
        `;
    }

    /**
     * Create error widget.
     * 
     * @param {string} message - Error message
     * @returns {string} HTML for error widget
     */
    createErrorWidget(message) {
        return `
            <div class="weather-widget bg-light text-center p-3">
                <i class="bi bi-cloud-slash text-muted" style="font-size: 2rem;"></i>
                <p class="text-muted mb-0 mt-2">${message}</p>
            </div>
        `;
    }

    /**
     * Get weather icon class based on condition.
     * 
     * @param {string} condition - Weather condition
     * @returns {string} Bootstrap icon class
     */
    getWeatherIcon(condition) {
        const iconMap = {
            // Clear conditions
            'clear': 'bi bi-sun',
            'sunny': 'bi bi-sun',
            
            // Cloudy conditions
            'clouds': 'bi bi-cloud',
            'cloudy': 'bi bi-cloud',
            'partly-cloudy': 'bi bi-cloud-sun',
            'overcast': 'bi bi-cloud-fill',
            
            // Rain conditions
            'rain': 'bi bi-cloud-rain',
            'drizzle': 'bi bi-cloud-drizzle',
            'light-rain': 'bi bi-cloud-drizzle',
            'heavy-rain': 'bi bi-cloud-rain-heavy',
            'thunderstorm': 'bi bi-cloud-lightning-rain',
            
            // Snow conditions
            'snow': 'bi bi-cloud-snow',
            'light-snow': 'bi bi-cloud-snow',
            'heavy-snow': 'bi bi-cloud-snow-fill',
            
            // Other conditions
            'mist': 'bi bi-cloud-haze',
            'fog': 'bi bi-cloud-fog',
            'haze': 'bi bi-cloud-haze',
            'wind': 'bi bi-wind',
            
            // Default
            'default': 'bi bi-cloud-sun'
        };

        const normalizedCondition = condition.toLowerCase().replace(/\s+/g, '-');
        return iconMap[normalizedCondition] || iconMap['default'];
    }

    /**
     * Get weather recommendation for activities.
     * 
     * @param {Object} weatherData - Weather data
     * @param {string} activityType - Type of activity
     * @returns {Object} Recommendation object
     */
    getActivityRecommendation(weatherData, activityType = 'general') {
        if (!weatherData || !weatherData.current) {
            return {
                suitable: true,
                recommendation: 'Weather data unavailable',
                level: 'neutral'
            };
        }

        const current = weatherData.current;
        const temp = current.temperature || 0;
        const condition = (current.condition || '').toLowerCase();
        const humidity = current.humidity || 0;

        // Temperature recommendations
        let tempRecommendation = this.getTemperatureRecommendation(temp, activityType);
        
        // Weather condition recommendations
        let conditionRecommendation = this.getConditionRecommendation(condition, activityType);
        
        // Combine recommendations
        const recommendations = [tempRecommendation, conditionRecommendation].filter(r => r.level !== 'neutral');
        
        if (recommendations.length === 0) {
            return {
                suitable: true,
                recommendation: 'Perfect weather for your activity!',
                level: 'good'
            };
        }

        // Return the most critical recommendation
        const critical = recommendations.find(r => r.level === 'bad');
        if (critical) return critical;

        const warning = recommendations.find(r => r.level === 'warning');
        if (warning) return warning;

        return recommendations[0];
    }

    /**
     * Get temperature-based recommendation.
     * 
     * @param {number} temp - Temperature in Celsius
     * @param {string} activityType - Activity type
     * @returns {Object} Temperature recommendation
     */
    getTemperatureRecommendation(temp, activityType) {
        const recommendations = {
            outdoor: {
                cold: { threshold: 5, message: 'Too cold for outdoor activities. Consider indoor alternatives.', level: 'bad' },
                cool: { threshold: 15, message: 'Cool weather - dress warmly for outdoor activities.', level: 'warning' },
                perfect: { min: 15, max: 28, message: 'Perfect temperature for outdoor activities!', level: 'good' },
                hot: { threshold: 35, message: 'Very hot - take breaks and stay hydrated.', level: 'warning' },
                extreme: { threshold: 40, message: 'Extremely hot - avoid outdoor activities during peak hours.', level: 'bad' }
            },
            indoor: {
                general: { message: 'Indoor activities are not significantly affected by temperature.', level: 'neutral' }
            }
        };

        const category = activityType.includes('sightseeing') || activityType.includes('outdoor') ? 'outdoor' : 'indoor';
        
        if (category === 'indoor') {
            return recommendations.indoor.general;
        }

        const outdoor = recommendations.outdoor;
        
        if (temp <= outdoor.cold.threshold) return outdoor.cold;
        if (temp <= outdoor.cool.threshold) return outdoor.cool;
        if (temp >= outdoor.extreme.threshold) return outdoor.extreme;
        if (temp >= outdoor.hot.threshold) return outdoor.hot;
        if (temp >= outdoor.perfect.min && temp <= outdoor.perfect.max) return outdoor.perfect;

        return { recommendation: 'Temperature is acceptable for outdoor activities.', level: 'neutral' };
    }

    /**
     * Get weather condition-based recommendation.
     * 
     * @param {string} condition - Weather condition
     * @param {string} activityType - Activity type
     * @returns {Object} Condition recommendation
     */
    getConditionRecommendation(condition, activityType) {
        const badConditions = ['thunderstorm', 'heavy-rain', 'heavy-snow'];
        const warningConditions = ['rain', 'drizzle', 'snow', 'fog'];
        
        if (badConditions.some(bad => condition.includes(bad))) {
            return {
                suitable: false,
                recommendation: 'Severe weather conditions - consider rescheduling outdoor activities.',
                level: 'bad'
            };
        }
        
        if (warningConditions.some(warning => condition.includes(warning))) {
            return {
                suitable: true,
                recommendation: 'Weather conditions may affect outdoor activities. Take precautions.',
                level: 'warning'
            };
        }
        
        return {
            suitable: true,
            recommendation: 'Weather conditions are favorable.',
            level: 'good'
        };
    }

    /**
     * Format weather data for display.
     * 
     * @param {Object} weatherData - Raw weather data
     * @returns {Object} Formatted weather data
     */
    formatWeatherData(weatherData) {
        if (!weatherData) return null;

        return {
            current: weatherData.current ? {
                temperature: Math.round(weatherData.current.temperature || 0),
                feelsLike: Math.round(weatherData.current.feels_like || 0),
                description: weatherData.current.description || 'Unknown',
                condition: weatherData.current.condition || 'clear',
                humidity: weatherData.current.humidity || 0,
                icon: this.getWeatherIcon(weatherData.current.condition || 'clear')
            } : null,
            
            forecast: (weatherData.daily_forecasts || []).map(day => ({
                date: day.date,
                dayName: new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' }),
                minTemp: Math.round(day.min_temp || 0),
                maxTemp: Math.round(day.max_temp || 0),
                condition: day.condition || 'clear',
                description: day.description || 'Unknown',
                icon: this.getWeatherIcon(day.condition || 'clear')
            })),
            
            location: weatherData.location || {}
        };
    }

    /**
     * Clear weather cache.
     */
    clearCache() {
        this.weatherCache.clear();
    }

    /**
     * Check if weather data indicates good conditions for outdoor activities.
     * 
     * @param {Object} weatherData - Weather data
     * @returns {boolean} Whether conditions are good for outdoor activities
     */
    isGoodForOutdoorActivities(weatherData) {
        const recommendation = this.getActivityRecommendation(weatherData, 'outdoor');
        return recommendation.level === 'good' || recommendation.level === 'neutral';
    }
}

/**
 * Weather widget component for easy integration.
 */
class WeatherWidget {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            showForecast: true,
            showDetails: true,
            compact: false,
            theme: 'light',
            autoRefresh: true,
            refreshInterval: 10 * 60 * 1000, // 10 minutes
            ...options
        };
        this.weatherUtils = new WeatherUtils();
        this.refreshTimer = null;
    }

    /**
     * Load and display weather data.
     * 
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     */
    async loadWeather(lat, lon) {
        try {
            this.showLoading();
            
            const weatherData = await this.weatherUtils.getWeatherData(lat, lon);
            
            if (weatherData) {
                this.displayWeather(weatherData);
                
                if (this.options.autoRefresh) {
                    this.startAutoRefresh(lat, lon);
                }
            } else {
                this.showError('Unable to load weather data');
            }
            
        } catch (error) {
            console.error('Error loading weather:', error);
            this.showError('Weather service temporarily unavailable');
        }
    }

    /**
     * Display weather data in the widget.
     * 
     * @param {Object} weatherData - Weather data to display
     */
    displayWeather(weatherData) {
        if (!this.container) return;
        
        const widgetHtml = this.weatherUtils.createWeatherWidget(weatherData, this.options);
        this.container.innerHTML = widgetHtml;
        
        // Add click handlers for forecast items
        this.addEventHandlers();
    }

    /**
     * Show loading state.
     */
    showLoading() {
        if (this.container) {
            this.container.innerHTML = `
                <div class="weather-widget bg-light text-center p-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="text-muted mb-0 mt-2">Loading weather...</p>
                </div>
            `;
        }
    }

    /**
     * Show error state.
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        if (this.container) {
            this.container.innerHTML = this.weatherUtils.createErrorWidget(message);
        }
    }

    /**
     * Add event handlers to widget elements.
     */
    addEventHandlers() {
        // Add hover effects, click handlers, etc.
        const forecastItems = this.container.querySelectorAll('.forecast-item');
        forecastItems.forEach(item => {
            item.style.cursor = 'pointer';
            item.addEventListener('mouseover', () => {
                item.style.backgroundColor = 'rgba(0,0,0,0.05)';
            });
            item.addEventListener('mouseout', () => {
                item.style.backgroundColor = 'transparent';
            });
        });
    }

    /**
     * Start auto-refresh timer.
     * 
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     */
    startAutoRefresh(lat, lon) {
        this.stopAutoRefresh();
        
        this.refreshTimer = setInterval(() => {
            this.loadWeather(lat, lon);
        }, this.options.refreshInterval);
    }

    /**
     * Stop auto-refresh timer.
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * Destroy the widget and clean up resources.
     */
    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Global weather utilities instance
const weatherUtils = new WeatherUtils();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        WeatherUtils,
        WeatherWidget,
        weatherUtils
    };
}