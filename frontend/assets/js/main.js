// Main JavaScript for ContentAI Pro Dashboard
// File: assets/js/main.js

// Navigation function for generator cards
// Add these to main.js if not present

// Navigation function for generator cards
function navigateToGenerator(type) {
    const routes = {
        'product': 'pages/product-generator.html',
        'social': 'pages/social-media.html',
        'blog': 'pages/blog-content.html',
        'marketing': 'pages/marketing-copy.html'
    };
    
    if (routes[type]) {
        window.location.href = routes[type];
    }
}

// Global showNotification function
window.showNotification = showNotification;

// Smooth scroll to generators section
function scrollToGenerators() {
    const generatorsSection = document.getElementById('generators');
    if (generatorsSection) {
        generatorsSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Show loading overlay during navigation
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    overlay.innerHTML = `
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span class="text-gray-700">Loading...</span>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Notification system
// Show notification function (add this to main.js)
function showNotification(message, type = 'info') {
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
    
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add hover effects to generator cards
function initializeCardEffects() {
    const cards = document.querySelectorAll('.generator-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Handle mobile menu toggle (for future mobile enhancements)
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('ContentAI Pro Dashboard initialized');
    
    // Initialize card hover effects
    initializeCardEffects();
    
    // Show welcome notification
    setTimeout(() => {
        showNotification('Welcome to ContentAI Pro! Select a generator to start creating content.', 'success');
    }, 1000);
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Handle browser back button
window.addEventListener('popstate', function(event) {
    // Handle navigation state if needed
    console.log('Navigation state changed');
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

// Utility functions
const Utils = {
    // Format date for display
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Generate unique ID
    generateId: function() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    },
    
    // Validate email
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            showNotification('Failed to copy text', 'error');
        });
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        navigateToGenerator,
        showNotification,
        Utils
    };
}