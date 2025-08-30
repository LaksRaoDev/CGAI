// Authentication utilities for all pages
// File: assets/js/auth.js

// Check if user is authenticated
function checkAuth() {
    const user = localStorage.getItem('user');
    if (!user) {
        showNotification('Please login to access this feature', 'warning');
        setTimeout(() => {
            window.location.href = '../auth.html';
        }, 1000);
        return false;
    }
    return true;
}

// Initialize user session on page load
function initializeAuth() {
    const user = localStorage.getItem('user');
    if (user) {
        const userData = JSON.parse(user);
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = userData.name;
        }
        return userData;
    }
    return null;
}

// Go back to main page
function goBack() {
    window.location.href = '../index.html';
}

// Logout function
function logout() {
    localStorage.removeItem('user');
    showNotification('Logged out successfully!', 'success');
    setTimeout(() => {
        window.location.href = '../auth.html';
    }, 1000);
}

// Common notification function
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
    
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

// Initialize authentication when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    const userData = initializeAuth();
    if (!userData) {
        checkAuth();
        return;
    }
    
    // Show welcome message
    setTimeout(() => {
        showNotification(`Welcome back, ${userData.name}!`, 'success');
    }, 500);
});
