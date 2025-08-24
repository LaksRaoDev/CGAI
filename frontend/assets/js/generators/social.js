// Updated Social Media Generator with Real API Integration
// File: frontend/assets/js/generators/social.js

// Global variables
let isGenerating = false;
let conversationHistory = [];
let selectedPlatform = 'facebook';

// Back navigation function
function goBack() {
    window.location.href = '../index.html';
}

// Platform selection
function selectPlatform(platform) {
    selectedPlatform = platform;
    
    // Remove selected class from all platforms
    document.querySelectorAll('.platform-btn').forEach(btn => {
        btn.classList.remove('platform-selected');
        btn.className = 'platform-btn p-3 border border-gray-200 rounded-lg text-gray-700 text-xs font-medium hover:border-gray-300 flex flex-col items-center transition';
    });
    
    // Add selected class to clicked platform
    const platformBtn = document.getElementById(`platform-${platform}`);
    platformBtn.classList.add('platform-selected');
    
    // Update styles based on platform
    const platformColors = {
        facebook: 'border-facebook bg-facebook/10 text-facebook',
        instagram: 'border-instagram bg-instagram/10 text-instagram',
        twitter: 'border-twitter bg-twitter/10 text-twitter',
        linkedin: 'border-linkedin bg-linkedin/10 text-linkedin'
    };
    
    platformBtn.className = `platform-btn p-3 border-2 ${platformColors[platform]} rounded-lg text-xs font-medium flex flex-col items-center transition platform-selected`;
}

// Quick suggestion function
function quickSuggestion(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}

// Get user settings
function getUserSettings() {
    return {
        platform: selectedPlatform,
        postType: document.querySelector('input[name="postType"]:checked').value,
        tone: document.getElementById('tone').value,
        length: document.getElementById('contentLength').value,
        audience: document.getElementById('targetAudience').value,
        autoHashtags: document.getElementById('autoHashtags').checked,
        customHashtags: document.getElementById('customHashtags').value,
        hashtagCount: document.getElementById('hashtagCount').value,
        includeCTA: document.getElementById('includeCTA').checked,
        includeQuestion: document.getElementById('includeQuestion').checked,
        includeEmojis: document.getElementById('includeEmojis').checked,
        includeMentions: document.getElementById('includeMentions').checked
    };
}

// Add message to chat interface
function addMessage(message, isUser = false, isLoading = false) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
    
    if (isUser) {
        messageDiv.innerHTML = `
            <div class="bg-secondary rounded-lg p-4 max-w-md text-white">
                <p>${message}</p>
            </div>
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <i class="ri-user-line text-gray-600 text-sm"></i>
            </div>
        `;
    } else if (isLoading) {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-md">
                <div class="flex items-center space-x-2">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-secondary"></div>
                    <span class="text-gray-600 text-sm">Creating post...</span>
                </div>
            </div>
        `;
        messageDiv.id = 'loadingMessage';
    } else {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-md">
                <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                    <div class="flex items-center space-x-2 mb-3">
                        <i class="ri-${getPlatformIcon()}-line text-lg text-${selectedPlatform}"></i>
                        <span class="text-sm font-medium text-gray-600">${selectedPlatform.charAt(0).toUpperCase() + selectedPlatform.slice(1)} Post</span>
                    </div>
                    <div class="text-gray-800 whitespace-pre-line">${message}</div>
                </div>
                <div class="flex items-center space-x-2 pt-3 border-t border-gray-200">
                    <button onclick="copyContent(this)" class="flex items-center space-x-1 px-3 py-1 bg-secondary text-white rounded-md text-sm hover:bg-secondary/90 transition">
                        <i class="ri-file-copy-line"></i>
                        <span>Copy</span>
                    </button>
                    <button onclick="regenerateContent()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-refresh-line"></i>
                        <span>Regenerate</span>
                    </button>
                    <button onclick="shareToSocial()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-share-line"></i>
                        <span>Share</span>
                    </button>
                </div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    return messageDiv;
}

// Get platform icon
function getPlatformIcon() {
    const icons = {
        facebook: 'facebook-fill',
        instagram: 'instagram-line',
        twitter: 'twitter-line',
        linkedin: 'linkedin-fill'
    };
    return icons[selectedPlatform] || 'smartphone-line';
}

// Scroll to bottom of chat
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Send message function with real API integration
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isGenerating) return;
    
    // Validate input
    const validation = Utils.validateInput(message, 5, 300);
    if (!validation.isValid) {
        showNotification(validation.errors[0], 'error');
        return;
    }
    
    // Add user message
    addMessage(message, true);
    messageInput.value = '';
    
    // Add loading message
    isGenerating = true;
    document.getElementById('sendBtn').disabled = true;
    const loadingMsg = addMessage('', false, true);
    
    try {
        // Get settings
        const settings = getUserSettings();
        
        // Make API call
        const response = await api.generateSocialPost(message, settings);
        const data = Utils.formatResponse(response);
        
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add response
        addMessage(data.content);
        
        // Store in conversation history
        conversationHistory.push({
            user: message,
            ai: data.content,
            settings: data.settings_used,
            timestamp: new Date().toISOString(),
            characterCount: data.character_count,
            platform: data.platform
        });
        
        // Success notification
        showNotification(`${selectedPlatform.charAt(0).toUpperCase() + selectedPlatform.slice(1)} post generated successfully!`, 'success');
        
    } catch (error) {
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Handle error
        Utils.handleError(error, 'Failed to generate social media post. Please check if the backend server is running.');
        
        // Add error message
        addMessage('Sorry, I encountered an error while generating the post. Please try again or check your connection.');
        
    } finally {
        isGenerating = false;
        document.getElementById('sendBtn').disabled = false;
    }
}

// Copy content function
async function copyContent(button) {
    const content = button.closest('.bg-gray-100').querySelector('.text-gray-800').textContent;
    
    const success = await Utils.copyToClipboard(content);
    if (success) {
        // Show success feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="ri-check-line"></i><span>Copied!</span>';
        button.classList.remove('bg-secondary');
        button.classList.add('bg-green-500');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-500');
            button.classList.add('bg-secondary');
        }, 2000);
    }
}

// Regenerate content function
async function regenerateContent() {
    if (conversationHistory.length === 0) {
        showNotification('No previous content to regenerate', 'warning');
        return;
    }
    
    const lastConversation = conversationHistory[conversationHistory.length - 1];
    const settings = getUserSettings();
    
    isGenerating = true;
    const loadingMsg = addMessage('', false, true);
    
    try {
        // Make API call with same input but current settings
        const response = await api.generateSocialPost(lastConversation.user, settings);
        const data = Utils.formatResponse(response);
        
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add new response
        addMessage(data.content);
        
        // Update conversation history
        conversationHistory[conversationHistory.length - 1] = {
            user: lastConversation.user,
            ai: data.content,
            settings: data.settings_used,
            timestamp: new Date().toISOString(),
            characterCount: data.character_count,
            platform: data.platform
        };
        
        showNotification('Post regenerated successfully!', 'success');
        
    } catch (error) {
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        Utils.handleError(error, 'Failed to regenerate content. Please try again.');
    } finally {
        isGenerating = false;
    }
}

// Share to social function
function shareToSocial() {
    showNotification('Direct sharing feature coming soon!', 'info');
}

// Generate sample function
function generateSample() {
    const samples = [
        "Weekend flash sale announcement - 50% off all electronics",
        "Customer success story and testimonial showcase",
        "New eco-friendly product line launch",
        "Behind the scenes office culture and team highlight",
        "Industry tips and educational content sharing",
        "Product demonstration and how-to tutorial",
        "Company milestone celebration post",
        "User-generated content feature and appreciation"
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    document.getElementById('messageInput').value = randomSample;
    sendMessage();
}

// Schedule post function
function schedulePost() {
    showNotification('Post scheduling feature coming soon!', 'info');
}

// Reset settings function
function resetSettings() {
    // Reset platform to Facebook
    selectPlatform('facebook');
    
    // Reset radio buttons
    document.querySelector('input[name="postType"][value="promotional"]').checked = true;
    
    // Reset dropdowns
    document.getElementById('tone').value = 'friendly';
    document.getElementById('contentLength').value = 'medium';
    document.getElementById('targetAudience').value = 'general';
    document.getElementById('hashtagCount').value = '5';
    
    // Reset checkboxes
    document.getElementById('autoHashtags').checked = true;
    document.getElementById('includeCTA').checked = true;
    document.getElementById('includeQuestion').checked = false;
    document.getElementById('includeEmojis').checked = true;
    document.getElementById('includeMentions').checked = false;
    
    // Clear custom hashtags
    document.getElementById('customHashtags').value = '';
    
    showNotification('Settings reset to default values', 'success');
}

// Check backend connection on page load
async function checkBackendConnection() {
    try {
        const isConnected = await Utils.checkBackendStatus();
        if (!isConnected) {
            showNotification('Backend server not connected. Please start the backend server.', 'warning');
        }
    } catch (error) {
        console.warn('Backend connection check failed:', error);
    }
}

// Load platform configurations from API
async function loadPlatformConfigs() {
    try {
        const response = await api.getSocialPlatforms();
        const data = Utils.formatResponse(response);
        
        // Update UI with platform information (if needed)
        console.log('Available platforms:', data.platforms);
        
        // You can use this data to update character limits, etc.
        // For example, show character count for selected platform
        
    } catch (error) {
        console.warn('Failed to load platform configurations:', error);
    }
}

// Validate input for selected platform
async function validateForPlatform(topic) {
    try {
        const response = await api.validateSocialInput(topic, selectedPlatform);
        const data = Utils.formatResponse(response);
        
        if (!data.valid && data.errors.length > 0) {
            showNotification(data.errors[0], 'warning');
            return false;
        }
        
        return true;
        
    } catch (error) {
        console.warn('Validation failed:', error);
        return true; // Continue if validation API fails
    }
}

// Update character count for platform
function updateCharacterCount() {
    const messageInput = document.getElementById('messageInput');
    const currentLength = messageInput.value.length;
    
    const platformLimits = {
        twitter: 280,
        instagram: 2200,
        facebook: 63206,
        linkedin: 3000
    };
    
    const limit = platformLimits[selectedPlatform] || 280;
    
    // You can add a character counter UI element here if needed
    if (currentLength > limit) {
        showNotification(`Content too long for ${selectedPlatform} (${currentLength}/${limit} characters)`, 'warning');
    }
}

// Enter key support
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Add character count update
        messageInput.addEventListener('input', updateCharacterCount);
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Social Media Generator loaded successfully!');
    
    // Focus on input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.focus();
    }
    
    // Set default platform
    selectPlatform('facebook');
    
    // Check backend connection
    checkBackendConnection();
    
    // Load platform configurations
    loadPlatformConfigs();
});