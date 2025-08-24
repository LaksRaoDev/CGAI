// Updated Product Description Generator with Real API Integration
// File: frontend/assets/js/generators/product.js

// Global variables
let isGenerating = false;
let conversationHistory = [];

// Back navigation function
function goBack() {
    window.location.href = '../index.html';
}

// Quick suggestion function
function quickSuggestion(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}

// Get user settings from the sidebar
function getUserSettings() {
    return {
        tone: document.querySelector('input[name="tone"]:checked').value,
        length: document.getElementById('contentLength').value,
        audience: document.getElementById('targetAudience').value,
        category: document.getElementById('productCategory').value,
        includeBenefits: document.getElementById('includeBenefits').checked,
        includeSpecs: document.getElementById('includeSpecs').checked,
        includeUseCases: document.getElementById('includeUseCases').checked,
        includeWarranty: document.getElementById('includeWarranty').checked,
        includeCTA: document.getElementById('includeCTA').checked,
        seoKeywords: document.getElementById('seoKeywords').checked,
        seoMeta: document.getElementById('seoMeta').checked
    };
}

// Add message to chat interface
function addMessage(message, isUser = false, isLoading = false) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
    
    if (isUser) {
        messageDiv.innerHTML = `
            <div class="bg-primary rounded-lg p-4 max-w-md text-white">
                <p>${message}</p>
            </div>
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <i class="ri-user-line text-gray-600 text-sm"></i>
            </div>
        `;
    } else if (isLoading) {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-md">
                <div class="flex items-center space-x-2">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    <span class="text-gray-600 text-sm">Generating description...</span>
                </div>
            </div>
        `;
        messageDiv.id = 'loadingMessage';
    } else {
        const wordCount = message.split(' ').length;
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-md">
                <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center space-x-2">
                            <i class="ri-shopping-bag-line text-lg text-blue-600"></i>
                            <span class="text-sm font-medium text-gray-600">Product Description</span>
                        </div>
                        <div class="text-xs text-gray-500">${wordCount} words</div>
                    </div>
                    <div class="text-gray-800 whitespace-pre-line">${message}</div>
                </div>
                <div class="flex items-center space-x-2 pt-3 border-t border-gray-200">
                    <button onclick="copyContent(this)" class="flex items-center space-x-1 px-3 py-1 bg-primary text-white rounded-md text-sm hover:bg-primary/90 transition">
                        <i class="ri-file-copy-line"></i>
                        <span>Copy</span>
                    </button>
                    <button onclick="regenerateContent()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-refresh-line"></i>
                        <span>Regenerate</span>
                    </button>
                    <button onclick="improveContent()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-edit-line"></i>
                        <span>Improve</span>
                    </button>
                </div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    return messageDiv;
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
    const validation = Utils.validateInput(message, 10, 500);
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
        const response = await api.generateProductDescription(message, settings);
        const data = Utils.formatResponse(response);
        
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add response
        addMessage(data.description);
        
        // Store in conversation history
        conversationHistory.push({
            user: message,
            ai: data.description,
            settings: data.settings_used,
            timestamp: new Date().toISOString(),
            wordCount: data.word_count
        });
        
        // Success notification
        showNotification('Product description generated successfully!', 'success');
        
    } catch (error) {
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Handle error
        Utils.handleError(error, 'Failed to generate product description. Please check if the backend server is running.');
        
        // Add error message
        addMessage('Sorry, I encountered an error while generating the description. Please try again or check your connection.');
        
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
        button.classList.remove('bg-primary');
        button.classList.add('bg-green-500');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-500');
            button.classList.add('bg-primary');
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
        const response = await api.generateProductDescription(lastConversation.user, settings);
        const data = Utils.formatResponse(response);
        
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add new response
        addMessage(data.description);
        
        // Update conversation history
        conversationHistory[conversationHistory.length - 1] = {
            user: lastConversation.user,
            ai: data.description,
            settings: data.settings_used,
            timestamp: new Date().toISOString(),
            wordCount: data.word_count
        };
        
        showNotification('Content regenerated successfully!', 'success');
        
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

// Improve content function
function improveContent() {
    showNotification('Content improvement feature coming soon!', 'info');
}

// Generate sample function
function generateSample() {
    const samples = [
        "Premium wireless noise-cancelling headphones with 30-hour battery life",
        "Ultra-lightweight gaming laptop with RTX 4070 and 144Hz display",
        "Organic anti-aging face serum with vitamin C and hyaluronic acid",
        "Smart fitness tracker with heart rate monitoring and GPS",
        "Portable Bluetooth speaker with waterproof design and 360-degree sound"
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    document.getElementById('messageInput').value = randomSample;
    sendMessage();
}

// Reset settings function
function resetSettings() {
    // Reset to default values
    document.querySelector('input[name="tone"][value="professional"]').checked = true;
    document.getElementById('contentLength').value = 'medium';
    document.getElementById('targetAudience').value = 'general';
    document.getElementById('productCategory').value = 'electronics';
    
    // Reset checkboxes
    document.getElementById('includeBenefits').checked = true;
    document.getElementById('includeSpecs').checked = true;
    document.getElementById('includeUseCases').checked = false;
    document.getElementById('includeWarranty').checked = false;
    document.getElementById('includeCTA').checked = true;
    document.getElementById('seoKeywords').checked = true;
    document.getElementById('seoMeta').checked = false;
    
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

// Load templates from API
async function loadTemplates() {
    try {
        const response = await api.getProductTemplates();
        const data = Utils.formatResponse(response);
        
        // Update UI with available options (if needed)
        console.log('Available templates:', data);
        
    } catch (error) {
        console.warn('Failed to load templates:', error);
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
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Product Description Generator loaded successfully!');
    
    // Focus on input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.focus();
    }
    
    // Check backend connection
    checkBackendConnection();
    
    // Load templates
    loadTemplates();
});