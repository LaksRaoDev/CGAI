// API Helper Functions for Content Generation AI
// File: frontend/assets/js/utils/helpers.js

// API Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:5000/api/v1',
    timeout: 30000, // 30 seconds
    headers: {
        'Content-Type': 'application/json',
    }
};

// API Helper Class
class APIHelper {
    constructor() {
        this.baseURL = API_CONFIG.baseURL;
        this.timeout = API_CONFIG.timeout;
        this.headers = API_CONFIG.headers;
    }

    // Generic API request method
    async makeRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method: method,
            headers: this.headers,
            signal: AbortSignal.timeout(this.timeout)
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError' || error.name === 'TimeoutError') {
                throw new Error('Request timeout. Please try again.');
            }
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Unable to connect to server. Please check if the backend is running.');
            }
            throw error;
        }
    }

    // Product Description API calls
    async generateProductDescription(productInfo, settings) {
        return await this.makeRequest('/product/generate', 'POST', {
            product_info: productInfo,
            settings: settings
        });
    }

    async getProductTemplates() {
        return await this.makeRequest('/product/templates');
    }

    async validateProductInput(productInfo) {
        return await this.makeRequest('/product/validate', 'POST', {
            product_info: productInfo
        });
    }

    // Social Media API calls
    async generateSocialPost(topic, settings) {
        return await this.makeRequest('/social/generate', 'POST', {
            topic: topic,
            settings: settings
        });
    }

    async getSocialPlatforms() {
        return await this.makeRequest('/social/platforms');
    }

    async validateSocialInput(topic, platform) {
        return await this.makeRequest('/social/validate', 'POST', {
            topic: topic,
            platform: platform
        });
    }

    // Blog Content API calls
    async generateBlogContent(topic, settings) {
        return await this.makeRequest('/blog/generate', 'POST', {
            topic: topic,
            settings: settings
        });
    }

    async getBlogTemplates() {
        return await this.makeRequest('/blog/templates');
    }

    async validateBlogInput(topic) {
        return await this.makeRequest('/blog/validate', 'POST', {
            topic: topic
        });
    }

    // Marketing Copy API calls
    async generateMarketingCopy(topic, settings) {
        return await this.makeRequest('/marketing/generate', 'POST', {
            topic: topic,
            settings: settings
        });
    }

    async getMarketingTemplates() {
        return await this.makeRequest('/marketing/templates');
    }

    async analyzeMarketingCopy(content) {
        return await this.makeRequest('/marketing/analyze', 'POST', {
            content: content
        });
    }

    async validateMarketingInput(topic, copyType) {
        return await this.makeRequest('/marketing/validate', 'POST', {
            topic: topic,
            copy_type: copyType
        });
    }

    // Health check
    async healthCheck() {
        return await this.makeRequest('/', 'GET');
    }

    // API status
    async getAPIStatus() {
        return await this.makeRequest('/status');
    }
}

// Create global API instance
const api = new APIHelper();

// Utility Functions
const Utils = {
    // Show loading state
    showLoading: function(element, message = 'Loading...') {
        if (element) {
            element.innerHTML = `
                <div class="flex items-center space-x-2">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    <span class="text-gray-600 text-sm">${message}</span>
                </div>
            `;
        }
    },

    // Hide loading state
    hideLoading: function(element, originalContent = '') {
        if (element) {
            element.innerHTML = originalContent;
        }
    },

    // Format API response for display
    formatResponse: function(response) {
        if (response.success && response.data) {
            return response.data;
        }
        throw new Error(response.error || 'Unknown error occurred');
    },

    // Handle API errors
    handleError: function(error, userMessage = 'Something went wrong. Please try again.') {
        console.error('API Error:', error);
        
        // Show user-friendly error message
        if (typeof showNotification === 'function') {
            showNotification(userMessage, 'error');
        } else {
            alert(userMessage);
        }
        
        return null;
    },

    // Validate input before API call
    validateInput: function(input, minLength = 5, maxLength = 500) {
        const errors = [];
        
        if (!input || typeof input !== 'string') {
            errors.push('Input is required');
        } else {
            const trimmed = input.trim();
            if (trimmed.length < minLength) {
                errors.push(`Input must be at least ${minLength} characters`);
            }
            if (trimmed.length > maxLength) {
                errors.push(`Input must be less than ${maxLength} characters`);
            }
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },

    // Debounce function for API calls
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Retry API call with exponential backoff
    retryWithBackoff: async function(apiCall, maxRetries = 3) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await apiCall();
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                
                const delay = Math.pow(2, i) * 1000; // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    },

    // Check if backend is running
    checkBackendStatus: async function() {
    try {
        // Use root endpoint instead of /api/v1/
        const response = await fetch('http://localhost:5000/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        return response.ok;
    } catch (error) {
        return false;
    }
    },

    // Copy text to clipboard
    copyToClipboard: async function(text) {
        try {
            await navigator.clipboard.writeText(text);
            if (typeof showNotification === 'function') {
                showNotification('Copied to clipboard!', 'success');
            }
            return true;
        } catch (error) {
            console.error('Copy failed:', error);
            if (typeof showNotification === 'function') {
                showNotification('Failed to copy text', 'error');
            }
            return false;
        }
    },

    // Format date for display
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Generate unique ID
    generateId: function() {
        return 'id_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    },

    // Storage helpers (localStorage wrapper)
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },

        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },

        remove: function(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        }
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIHelper, api, Utils };
}


// Make showNotification globally available
window.showNotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 z-50 px-4 py-3 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
    
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500', 
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    }[type] || 'bg-blue-500';
    
    notification.classList.add(bgColor);
    notification.innerHTML = `
        <div class="flex items-center space-x-2 text-white">
            <i class="ri-information-line"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.remove('translate-x-full'), 100);
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};