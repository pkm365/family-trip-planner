/**
 * Family Trip Planner - Core JavaScript Functions
 * 
 * Provides common utilities and API functions used across all pages.
 */

// Global configuration
const CONFIG = {
    API_BASE_URL: '',  // Same domain
    ALERT_TIMEOUT: 5000,  // 5 seconds
    LOADING_TIMEOUT: 30000  // 30 seconds
};

/**
 * Make API requests with proper error handling and loading states.
 * 
 * @param {string} endpoint - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise} API response data
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Handle empty responses (like DELETE)
        if (response.status === 204) {
            return null;
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

/**
 * Show loading spinner.
 * 
 * @param {boolean} show - Whether to show or hide the spinner
 */
function showLoading(show = true) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        if (show) {
            spinner.classList.remove('d-none');
        } else {
            spinner.classList.add('d-none');
        }
    }
}

/**
 * Show alert message to the user.
 * 
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {number} timeout - Auto-dismiss timeout in milliseconds
 */
function showAlert(message, type = 'info', timeout = CONFIG.ALERT_TIMEOUT) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.warn('Alert container not found');
        return;
    }
    
    const alertId = `alert-${Date.now()}`;
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
            <i class="bi bi-${getAlertIcon(type)}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after timeout
    if (timeout > 0) {
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, timeout);
    }
    
    // Scroll to top to ensure alert is visible
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Get Bootstrap icon for alert type.
 * 
 * @param {string} type - Alert type
 * @returns {string} Icon name
 */
function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Format date string for display.
 * 
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format datetime string for display.
 * 
 * @param {string} datetimeString - ISO datetime string
 * @returns {string} Formatted datetime
 */
function formatDateTime(datetimeString) {
    if (!datetimeString) return '';
    
    const date = new Date(datetimeString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Debounce function calls.
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Validate form inputs.
 * 
 * @param {HTMLFormElement} form - Form to validate
 * @returns {boolean} Whether form is valid
 */
function validateForm(form) {
    if (!form.checkValidity()) {
        form.reportValidity();
        return false;
    }
    return true;
}

/**
 * Reset form and clear validation states.
 * 
 * @param {HTMLFormElement} form - Form to reset
 */
function resetForm(form) {
    form.reset();
    form.classList.remove('was-validated');
    
    // Clear custom validation messages
    form.querySelectorAll('.invalid-feedback').forEach(feedback => {
        feedback.textContent = '';
    });
    
    form.querySelectorAll('.is-invalid').forEach(input => {
        input.classList.remove('is-invalid');
    });
}

/**
 * Get category color class for badges.
 * 
 * @param {string} category - Activity category
 * @returns {string} Bootstrap color class
 */
function getCategoryColor(category) {
    const colors = {
        sightseeing: 'primary',
        food: 'success',
        shopping: 'warning',
        rest: 'info',
        transportation: 'secondary'
    };
    return colors[category] || 'secondary';
}

/**
 * Get priority color class for badges.
 * 
 * @param {string} priority - Activity priority
 * @returns {string} Bootstrap color class
 */
function getPriorityColor(priority) {
    const colors = {
        must_do: 'danger',
        would_like: 'primary',
        optional: 'secondary'
    };
    return colors[priority] || 'secondary';
}

/**
 * Sanitize HTML to prevent XSS.
 * 
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
function sanitizeHtml(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}

/**
 * Copy text to clipboard.
 * 
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copied to clipboard!', 'success', 2000);
        return true;
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        showAlert('Failed to copy to clipboard', 'danger', 3000);
        return false;
    }
}

/**
 * Get URL parameter value.
 * 
 * @param {string} name - Parameter name
 * @returns {string|null} Parameter value
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Update URL parameter without page reload.
 * 
 * @param {string} name - Parameter name
 * @param {string} value - Parameter value
 */
function updateUrlParameter(name, value) {
    const url = new URL(window.location);
    url.searchParams.set(name, value);
    window.history.replaceState({}, '', url);
}

/**
 * Remove URL parameter without page reload.
 * 
 * @param {string} name - Parameter name
 */
function removeUrlParameter(name) {
    const url = new URL(window.location);
    url.searchParams.delete(name);
    window.history.replaceState({}, '', url);
}

/**
 * Initialize tooltips for elements with data-bs-toggle="tooltip".
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize popovers for elements with data-bs-toggle="popover".
 */
function initializePopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverTriggerList.forEach(popoverTriggerEl => {
        new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Format currency value.
 * 
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Calculate days between two dates.
 * 
 * @param {string|Date} startDate - Start date
 * @param {string|Date} endDate - End date
 * @returns {number} Number of days
 */
function daysBetween(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * Check if date is today.
 * 
 * @param {string|Date} date - Date to check
 * @returns {boolean} Whether date is today
 */
function isToday(date) {
    const today = new Date();
    const checkDate = new Date(date);
    
    return today.toDateString() === checkDate.toDateString();
}

/**
 * Get relative time string (e.g., "2 days ago", "in 3 hours").
 * 
 * @param {string|Date} date - Date to compare
 * @returns {string} Relative time string
 */
function getRelativeTime(date) {
    const now = new Date();
    const targetDate = new Date(date);
    const diffMs = targetDate - now;
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return 'Today';
    } else if (diffDays === 1) {
        return 'Tomorrow';
    } else if (diffDays === -1) {
        return 'Yesterday';
    } else if (diffDays > 0) {
        return `In ${diffDays} days`;
    } else {
        return `${Math.abs(diffDays)} days ago`;
    }
}

/**
 * Initialize common page functionality.
 */
function initializePage() {
    // Initialize Bootstrap components
    initializeTooltips();
    initializePopovers();
    
    // Set up global error handler
    window.addEventListener('unhandledrejection', event => {
        console.error('Unhandled promise rejection:', event.reason);
        showAlert('An unexpected error occurred. Please try again.', 'danger');
    });
    
    // Set up navigation active states
    updateNavigationState();
}

/**
 * Update navigation active states based on current page.
 */
function updateNavigationState() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ================================
// FAMILY FUNCTIONALITY
// ================================

/**
 * Load and display family members for the current trip
 */
async function loadFamilyMembers(tripId) {
    if (!tripId) return;
    
    try {
        const familyMembers = await apiRequest(`/api/family-members/?trip_id=${tripId}`);
        displayFamilyMembers(familyMembers);
        updateFamilyWishlistSummary(familyMembers);
        
        // Show family corner if there are members
        const familyCorner = document.getElementById('familyCorner');
        if (familyCorner) {
            familyCorner.classList.remove('d-none');
            familyCorner.classList.add('fade-in');
        }
        
    } catch (error) {
        console.error('Error loading family members:', error);
        showAlert('Failed to load family members', 'warning');
    }
}

/**
 * Display family member cards
 */
function displayFamilyMembers(familyMembers) {
    const container = document.getElementById('familyMembersContainer');
    const countBadge = document.getElementById('familyCount');
    
    if (!container || !countBadge) return;
    
    countBadge.textContent = familyMembers.length;
    
    if (familyMembers.length === 0) {
        container.innerHTML = `
            <div class="no-family-members text-center py-4">
                <i class="bi bi-people text-muted fs-1"></i>
                <p class="text-muted mt-2">No family members added yet.<br>Click "Add Family Member" to get started!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = familyMembers.map(member => createFamilyMemberCard(member)).join('');
}

/**
 * Create HTML for a family member card
 */
function createFamilyMemberCard(member) {
    const wishlistItems = parseFamilyWishlist(member.wishlist_items);
    const avatar = member.name.charAt(0).toUpperCase();
    const ageText = member.age ? ` (${member.age})` : '';
    
    return `
        <div class="family-member-card role-${member.role}" data-member-id="${member.id}">
            <div class="member-avatar" style="background: ${getMemberAvatarColor(member.role)}">
                ${avatar}
            </div>
            <div class="member-name">${member.name}${ageText}</div>
            <div class="member-role role-${member.role}">${member.role}</div>
            
            ${member.interests ? `
                <div class="member-interests mb-2">
                    <small class="text-muted"><i class="bi bi-heart-fill me-1"></i>Interests:</small>
                    <div class="small">${member.interests}</div>
                </div>
            ` : ''}
            
            ${wishlistItems.length > 0 ? `
                <div class="member-wishlist">
                    <small class="text-muted mb-2 d-block"><i class="bi bi-star-fill me-1"></i>Wishes:</small>
                    ${wishlistItems.slice(0, 3).map(item => `
                        <div class="wishlist-item">
                            <div class="priority-badge priority-${item.priority}"></div>
                            <span>${item.name}</span>
                        </div>
                    `).join('')}
                    ${wishlistItems.length > 3 ? `
                        <div class="small text-muted mt-1">+${wishlistItems.length - 3} more wishes</div>
                    ` : ''}
                </div>
            ` : ''}
            
            <div class="member-actions mt-2">
                <button class="btn btn-sm btn-warm-outline" onclick="editFamilyMember(${member.id})">
                    <i class="bi bi-pencil-fill"></i> Edit
                </button>
            </div>
        </div>
    `;
}

/**
 * Get avatar gradient color based on member role
 */
function getMemberAvatarColor(role) {
    const colors = {
        parent: 'linear-gradient(135deg, var(--warm-primary), #ff5252)',
        child: 'linear-gradient(135deg, var(--warm-accent), #ffd43b)',
        adult: 'linear-gradient(135deg, var(--warm-secondary), #3bc9db)'
    };
    return colors[role] || colors.adult;
}

/**
 * Parse family member wishlist from JSON string
 */
function parseFamilyWishlist(wishlistStr) {
    if (!wishlistStr) return [];
    
    try {
        const parsed = JSON.parse(wishlistStr);
        return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
        // If it's a simple string, convert to array
        return wishlistStr.split(',').map(item => ({
            name: item.trim(),
            priority: 'would_like'
        })).filter(item => item.name);
    }
}

/**
 * Update the family wishlist summary section
 */
function updateFamilyWishlistSummary(familyMembers) {
    const container = document.getElementById('familyWishlistSummary');
    if (!container) return;
    
    const allWishes = [];
    familyMembers.forEach(member => {
        const wishes = parseFamilyWishlist(member.wishlist_items);
        wishes.forEach(wish => {
            wish.memberName = member.name;
            allWishes.push(wish);
        });
    });
    
    if (allWishes.length === 0) {
        container.innerHTML = '<p class="text-muted small mb-0">No family wishes added yet</p>';
        return;
    }
    
    // Group by priority and show top wishes
    const priorityOrder = ['must_do', 'would_like', 'optional'];
    const sortedWishes = allWishes.sort((a, b) => {
        return priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority);
    });
    
    container.innerHTML = sortedWishes.slice(0, 8).map(wish => `
        <div class="wishlist-summary-item" title="${wish.memberName}'s wish">
            <span class="priority-badge priority-${wish.priority} me-2"></span>
            ${wish.name}
        </div>
    `).join('');
    
    if (allWishes.length > 8) {
        container.innerHTML += `<div class="small text-muted mt-2">+${allWishes.length - 8} more family wishes</div>`;
    }
}

/**
 * Edit family member (placeholder for modal functionality)
 */
function editFamilyMember(memberId) {
    console.log('Edit family member:', memberId);
    showAlert('Family member editing coming soon!', 'info');
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePage);

// Export functions for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        apiRequest,
        showLoading,
        showAlert,
        formatDate,
        formatDateTime,
        debounce,
        validateForm,
        resetForm,
        getCategoryColor,
        getPriorityColor,
        sanitizeHtml,
        copyToClipboard,
        getUrlParameter,
        updateUrlParameter,
        removeUrlParameter,
        formatCurrency,
        daysBetween,
        isToday,
        getRelativeTime
    };
}