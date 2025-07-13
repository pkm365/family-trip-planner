/**
 * Family Trip Planner - Internationalization (i18n) System
 * 
 * Provides language switching functionality for English and Chinese support.
 */

// Language configuration
const LANGUAGES = {
    en: {
        name: 'English',
        flag: '🇺🇸',
        code: 'en'
    },
    zh: {
        name: '中文',
        flag: '🇨🇳',
        code: 'zh'
    }
};

// Translation strings
const TRANSLATIONS = {
    en: {
        // Navigation
        'nav.dashboard': 'Dashboard',
        'nav.discovery': 'Discovery',
        'nav.daily_planner': 'Daily Planner',
        'nav.map_view': 'Map View',
        'nav.api_docs': 'API Docs',
        'nav.language': 'Language',
        
        // Common UI
        'common.loading': 'Loading...',
        'common.save': 'Save',
        'common.cancel': 'Cancel',
        'common.edit': 'Edit',
        'common.delete': 'Delete',
        'common.add': 'Add',
        'common.close': 'Close',
        'common.confirm': 'Confirm',
        'common.yes': 'Yes',
        'common.no': 'No',
        'common.clear': 'Clear',
        
        // Trip Management
        'trip.title': 'Family Trip Planner',
        'trip.new_trip': 'New Trip',
        'trip.edit_trip': 'Edit Trip',
        'trip.create_new_trip': 'Create New Trip',
        'trip.create_trip': 'Create Trip',
        'trip.trip_name': 'Trip Name',
        'trip.destination': 'Destination',
        'trip.start_date': 'Start Date',
        'trip.end_date': 'End Date',
        'trip.budget': 'Budget',
        'trip.accommodation': 'Accommodation',
        'trip.no_trips': 'No trips found. Create your first trip!',
        
        // Activities
        'activity.add_activity': 'Add Activity',
        'activity.edit_activity': 'Edit Activity',
        'activity.activity_name': 'Activity Name',
        'activity.description': 'Description',
        'activity.category': 'Category',
        'activity.priority': 'Priority',
        'activity.estimated_cost': 'Estimated Cost',
        'activity.time_slot': 'Time Slot',
        'activity.location': 'Location',
        'activity.location_name': 'Location Name',
        'activity.address': 'Address',
        'activity.notes': 'Notes',
        'activity.date': 'Date',
        
        // Categories
        'category.sightseeing': 'Sightseeing',
        'category.food': 'Food',
        'category.shopping': 'Shopping',
        'category.rest': 'Rest',
        'category.transportation': 'Transportation',
        
        // Priorities
        'priority.must_do': 'Must Do',
        'priority.would_like': 'Would Like',
        'priority.optional': 'Optional',
        
        // Time Slots
        'time.morning': 'Morning',
        'time.afternoon': 'Afternoon',
        'time.evening': 'Evening',
        
        // Discovery Hub
        'discovery.title': 'Activity Discovery',
        'discovery.search_activities': 'Search Activities',
        'discovery.search_query': 'Search Query',
        'discovery.search_placeholder': 'e.g., family restaurants, temples, shopping',
        'discovery.max_budget': 'Max Budget',
        'discovery.search': 'Search',
        'discovery.search_results': 'Search Results',
        'discovery.card_view': 'Cards',
        'discovery.list_view': 'List',
        'discovery.searching': 'Searching for activities...',
        'discovery.no_results': 'No activities found',
        'discovery.try_different_search': 'Try a different search term or adjust your filters.',
        'discovery.add_to_schedule': 'Add to Schedule',
        
        // Voting System
        'voting.family_votes': 'Family Votes',
        'voting.cast_vote': 'Cast Vote',
        'voting.like': 'Like',
        'voting.dislike': 'Dislike',
        'voting.neutral': 'Neutral',
        'voting.vote_score': 'Vote Score',
        'voting.votes_cast': 'Votes Cast',
        'voting.participation': 'Participation',
        
        // Favorites System
        'favorites.my_favorites': 'My Favorites',
        'favorites.add_to_favorites': 'Add to Favorites',
        'favorites.remove_from_favorites': 'Remove from Favorites',
        'favorites.favorite_added': 'Added to Favorites',
        'favorites.favorite_removed': 'Removed from Favorites',
        'favorites.no_favorites': 'No favorites yet',
        'favorites.sort_by_date': 'Sort by Date',
        'favorites.sort_by_rating': 'Sort by Rating',
        'favorites.sort_by_cost': 'Sort by Cost',
        
        // Sidebar
        'sidebar.all_activities': 'All Activities',
        
        // Family Management
        'family.our_journey': 'Our Family Journey',
        'family.add_member': 'Add Family Member',
        'family.edit_member': 'Edit Family Member',
        'family.member_name': 'Name',
        'family.member_age': 'Age',
        'family.member_role': 'Role',
        'family.member_interests': 'Interests & Hobbies',
        'family.member_wishes': 'Travel Wishes',
        'family.member_dietary': 'Dietary Restrictions',
        'family.member_mobility': 'Mobility Needs',
        'family.member_notes': 'Additional Notes',
        'family.wishes_dreams': 'Family Wishes & Dreams',
        'family.no_wishes': 'No family wishes added yet',
        'family.select_role': 'Select role...',
        'family.interests_placeholder': 'e.g., Photography, Museums, Adventure sports...',
        'family.wishes_placeholder': 'What would this family member love to see or do? (one per line)',
        'family.wishes_help': 'Enter each wish on a new line',
        'family.dietary_placeholder': 'e.g., Vegetarian, Gluten-free...',
        'family.mobility_placeholder': 'Any accessibility requirements...',
        'family.notes_placeholder': 'Any other important information...',
        'family.role_parent': 'Parent',
        'family.role_child': 'Child',
        'family.role_adult': 'Adult',
        'family.add_success': 'added to the family!',
        'family.update_success': 'Family member updated successfully!',
        'family.add_photo': 'Add Photo',
        'family.change_photo': 'Change Photo',
        'family.upload_image': 'Upload Image',
        
        // Messages
        'message.success': 'Operation completed successfully!',
        'message.error': 'An error occurred. Please try again.',
        'message.copied': 'Copied to clipboard!',
        'message.no_results': 'No results found.',
        
        // Weather
        'weather.current': 'Current Weather',
        'weather.forecast': 'Weather Forecast',
        'weather.temperature': 'Temperature',
        'weather.humidity': 'Humidity',
        'weather.wind': 'Wind',
        
        // Dashboard
        'dashboard.trip_overview': 'Trip Overview',
        'dashboard.total_trips': 'Total Trips',
        'dashboard.activities': 'Activities',
        'dashboard.family_members': 'Family Members',
        'dashboard.total_budget': 'Total Budget',
        'dashboard.recent_activities': 'Recent Activities',
        'dashboard.no_activities': 'No activities planned yet.',
        'dashboard.weather_update': 'Weather Update',
        'dashboard.weather_placeholder': 'Weather data will appear when you add a trip destination.',
        
        // Footer
        'footer.copyright': '© 2024 Family Trip Planner. Built with FastAPI, Bootstrap, and Leaflet.',
        'footer.weather_data': 'Weather data from',
        'footer.maps_from': 'Maps from'
    },
    zh: {
        // Navigation
        'nav.dashboard': '仪表板',
        'nav.discovery': '发现',
        'nav.daily_planner': '每日计划',
        'nav.map_view': '地图视图',
        'nav.api_docs': 'API 文档',
        'nav.language': '语言',
        
        // Common UI
        'common.loading': '加载中...',
        'common.save': '保存',
        'common.cancel': '取消',
        'common.edit': '编辑',
        'common.delete': '删除',
        'common.add': '添加',
        'common.close': '关闭',
        'common.confirm': '确认',
        'common.yes': '是',
        'common.no': '否',
        'common.clear': '清除',
        
        // Trip Management
        'trip.title': '家庭旅行计划',
        'trip.new_trip': '新建旅行',
        'trip.edit_trip': '编辑旅行',
        'trip.create_new_trip': '创建新旅行',
        'trip.create_trip': '创建旅行',
        'trip.trip_name': '旅行名称',
        'trip.destination': '目的地',
        'trip.start_date': '开始日期',
        'trip.end_date': '结束日期',
        'trip.budget': '预算',
        'trip.accommodation': '住宿',
        'trip.no_trips': '未找到旅行记录。创建您的第一个旅行！',
        
        // Activities
        'activity.add_activity': '添加活动',
        'activity.edit_activity': '编辑活动',
        'activity.activity_name': '活动名称',
        'activity.description': '描述',
        'activity.category': '类别',
        'activity.priority': '优先级',
        'activity.estimated_cost': '预估费用',
        'activity.time_slot': '时间段',
        'activity.location': '位置',
        'activity.location_name': '地点名称',
        'activity.address': '地址',
        'activity.notes': '备注',
        'activity.date': '日期',
        
        // Categories
        'category.sightseeing': '观光',
        'category.food': '餐饮',
        'category.shopping': '购物',
        'category.rest': '休息',
        'category.transportation': '交通',
        
        // Priorities
        'priority.must_do': '必做',
        'priority.would_like': '想做',
        'priority.optional': '可选',
        
        // Time Slots
        'time.morning': '上午',
        'time.afternoon': '下午',
        'time.evening': '晚上',
        
        // Discovery Hub
        'discovery.title': '活动发现',
        'discovery.search_activities': '搜索活动',
        'discovery.search_query': '搜索关键词',
        'discovery.search_placeholder': '例如：家庭餐厅、寺庙、购物',
        'discovery.max_budget': '最大预算',
        'discovery.search': '搜索',
        'discovery.search_results': '搜索结果',
        'discovery.card_view': '卡片视图',
        'discovery.list_view': '列表视图',
        'discovery.searching': '正在搜索活动...',
        'discovery.no_results': '未找到活动',
        'discovery.try_different_search': '尝试使用不同的搜索词或调整筛选条件。',
        'discovery.add_to_schedule': '添加到日程',
        
        // Voting System
        'voting.family_votes': '家庭投票',
        'voting.cast_vote': '投票',
        'voting.like': '喜欢',
        'voting.dislike': '不喜欢',
        'voting.neutral': '中性',
        'voting.vote_score': '投票得分',
        'voting.votes_cast': '已投票数',
        'voting.participation': '参与度',
        
        // Favorites System
        'favorites.my_favorites': '我的收藏',
        'favorites.add_to_favorites': '添加到收藏',
        'favorites.remove_from_favorites': '取消收藏',
        'favorites.favorite_added': '已添加到收藏',
        'favorites.favorite_removed': '已取消收藏',
        'favorites.no_favorites': '还没有收藏',
        'favorites.sort_by_date': '按时间排序',
        'favorites.sort_by_rating': '按评分排序',
        'favorites.sort_by_cost': '按费用排序',
        
        // Sidebar
        'sidebar.all_activities': '所有活动',
        
        // Family Management
        'family.our_journey': '我们的家庭旅程',
        'family.add_member': '添加家庭成员',
        'family.edit_member': '编辑家庭成员',
        'family.member_name': '姓名',
        'family.member_age': '年龄',
        'family.member_role': '角色',
        'family.member_interests': '兴趣爱好',
        'family.member_wishes': '旅行愿望',
        'family.member_dietary': '饮食限制',
        'family.member_mobility': '行动需求',
        'family.member_notes': '附加备注',
        'family.wishes_dreams': '家庭愿望与梦想',
        'family.no_wishes': '还没有添加家庭愿望',
        'family.select_role': '选择角色...',
        'family.interests_placeholder': '例如：摄影、博物馆、冒险运动...',
        'family.wishes_placeholder': '这位家庭成员想要看到或做什么？（每行一个）',
        'family.wishes_help': '每行输入一个愿望',
        'family.dietary_placeholder': '例如：素食主义者、无麸质...',
        'family.mobility_placeholder': '任何无障碍要求...',
        'family.notes_placeholder': '任何其他重要信息...',
        'family.role_parent': '父母',
        'family.role_child': '孩子',
        'family.role_adult': '成人',
        'family.add_success': '已添加到家庭！',
        'family.update_success': '家庭成员更新成功！',
        'family.add_photo': '添加照片',
        'family.change_photo': '更换照片',
        'family.upload_image': '上传图片',
        
        // Messages
        'message.success': '操作成功完成！',
        'message.error': '发生错误，请重试。',
        'message.copied': '已复制到剪贴板！',
        'message.no_results': '未找到结果。',
        
        // Weather
        'weather.current': '当前天气',
        'weather.forecast': '天气预报',
        'weather.temperature': '温度',
        'weather.humidity': '湿度',
        'weather.wind': '风速',
        
        // Dashboard
        'dashboard.trip_overview': '旅行概览',
        'dashboard.total_trips': '总旅行数',
        'dashboard.activities': '活动',
        'dashboard.family_members': '家庭成员',
        'dashboard.total_budget': '总预算',
        'dashboard.recent_activities': '最近活动',
        'dashboard.no_activities': '还没有计划活动。',
        'dashboard.weather_update': '天气更新',
        'dashboard.weather_placeholder': '添加旅行目的地后，天气数据将显示在这里。',
        
        // Footer
        'footer.copyright': '© 2024 家庭旅行计划。使用 FastAPI、Bootstrap 和 Leaflet 构建。',
        'footer.weather_data': '天气数据来自',
        'footer.maps_from': '地图来自'
    }
};

// Current language state
let currentLanguage = 'en';

/**
 * Get current language.
 * 
 * @returns {string} Current language code
 */
function getCurrentLanguage() {
    return currentLanguage;
}

/**
 * Set current language.
 * 
 * @param {string} lang - Language code (en/zh)
 */
function setCurrentLanguage(lang) {
    if (LANGUAGES[lang]) {
        currentLanguage = lang;
        localStorage.setItem('language', lang);
        
        // Update HTML lang attribute
        document.documentElement.lang = lang;
        
        // Update all translatable elements
        updateTranslations();
        
        // Trigger language change event
        const event = new CustomEvent('languageChanged', { detail: { language: lang } });
        document.dispatchEvent(event);
    }
}

/**
 * Get translation for a key.
 * 
 * @param {string} key - Translation key
 * @param {string} lang - Language code (optional, uses current language)
 * @returns {string} Translated text
 */
function t(key, lang = currentLanguage) {
    const translations = TRANSLATIONS[lang] || TRANSLATIONS['en'];
    return translations[key] || key;
}

/**
 * Update all translatable elements on the page.
 */
function updateTranslations() {
    // Update elements with data-i18n attribute
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        if (element.tagName === 'INPUT' && element.type === 'submit') {
            element.value = translation;
        } else if (element.tagName === 'INPUT' && element.hasAttribute('placeholder')) {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });
    
    // Update elements with data-i18n-attr attribute for other attributes
    const attrElements = document.querySelectorAll('[data-i18n-attr]');
    attrElements.forEach(element => {
        const attrConfig = element.getAttribute('data-i18n-attr');
        const [attr, key] = attrConfig.split(':');
        const translation = t(key);
        element.setAttribute(attr, translation);
    });
}

/**
 * Initialize internationalization system.
 */
function initializeI18n() {
    // Load saved language preference
    const savedLanguage = localStorage.getItem('language') || 'en';
    currentLanguage = savedLanguage;
    
    // Set HTML lang attribute
    document.documentElement.lang = currentLanguage;
    
    // Update translations
    updateTranslations();
    
    // Initialize language selector
    initializeLanguageSelector();
}

/**
 * Initialize language selector in navigation.
 */
function initializeLanguageSelector() {
    const navbar = document.querySelector('.navbar-nav');
    if (!navbar) return;
    
    // Create language selector dropdown
    const languageSelector = document.createElement('li');
    languageSelector.className = 'nav-item dropdown';
    
    const currentLang = LANGUAGES[currentLanguage];
    languageSelector.innerHTML = `
        <a class="nav-link dropdown-toggle" href="#" id="languageDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            <span class="language-flag">${currentLang.flag}</span>
            <span class="language-name">${currentLang.name}</span>
        </a>
        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
            ${Object.entries(LANGUAGES).map(([code, lang]) => `
                <li>
                    <a class="dropdown-item language-option ${code === currentLanguage ? 'active' : ''}" 
                       href="#" 
                       data-lang="${code}">
                        <span class="language-flag">${lang.flag}</span>
                        ${lang.name}
                    </a>
                </li>
            `).join('')}
        </ul>
    `;
    
    // Find the right position to insert (before API docs)
    const apiDocsItem = navbar.querySelector('a[href="/api/docs"]')?.parentElement;
    if (apiDocsItem) {
        navbar.insertBefore(languageSelector, apiDocsItem);
    } else {
        navbar.appendChild(languageSelector);
    }
    
    // Add click handlers for language options
    languageSelector.addEventListener('click', (e) => {
        if (e.target.classList.contains('language-option')) {
            e.preventDefault();
            const lang = e.target.getAttribute('data-lang');
            setCurrentLanguage(lang);
            updateLanguageSelector();
        }
    });
}

/**
 * Update language selector to reflect current language.
 */
function updateLanguageSelector() {
    const dropdown = document.getElementById('languageDropdown');
    if (!dropdown) return;
    
    const currentLang = LANGUAGES[currentLanguage];
    const flagSpan = dropdown.querySelector('.language-flag');
    const nameSpan = dropdown.querySelector('.language-name');
    
    if (flagSpan) flagSpan.textContent = currentLang.flag;
    if (nameSpan) nameSpan.textContent = currentLang.name;
    
    // Update active state in dropdown
    const options = dropdown.parentElement.querySelectorAll('.language-option');
    options.forEach(option => {
        option.classList.toggle('active', option.getAttribute('data-lang') === currentLanguage);
    });
}

/**
 * Get list of available languages.
 * 
 * @returns {Object} Available languages
 */
function getAvailableLanguages() {
    return LANGUAGES;
}

/**
 * Detect browser language and set if supported.
 */
function detectAndSetLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    const langCode = browserLang.split('-')[0]; // Get base language code
    
    if (LANGUAGES[langCode] && !localStorage.getItem('language')) {
        setCurrentLanguage(langCode);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    detectAndSetLanguage();
    initializeI18n();
});

// Export functions for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCurrentLanguage,
        setCurrentLanguage,
        t,
        updateTranslations,
        getAvailableLanguages,
        LANGUAGES,
        TRANSLATIONS
    };
}