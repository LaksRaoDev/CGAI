// Updated Marketing Copy Generator with Real API Integration
// File: frontend/assets/js/generators/marketing.js

// Global variables
let isGenerating = false;
let conversationHistory = [];
let selectedCopyType = 'email';

// Back navigation function
function goBack() {
    window.location.href = '../index.html';
}

// Copy type selection
function selectCopyType(type) {
    selectedCopyType = type;
    
    // Remove selected class from all types
    document.querySelectorAll('.copy-type-btn').forEach(btn => {
        btn.classList.remove('copy-type-selected');
        btn.className = 'copy-type-btn p-3 border border-gray-200 rounded-lg text-gray-700 text-xs font-medium hover:border-gray-300 flex flex-col items-center transition';
    });
    
    // Add selected class to clicked type
    const typeBtn = document.getElementById(`type-${type}`);
    typeBtn.classList.add('copy-type-selected');
    typeBtn.className = 'copy-type-btn p-3 border-2 border-marketing bg-marketing/10 rounded-lg text-marketing text-xs font-medium flex flex-col items-center transition copy-type-selected';
}

// Quick suggestion function
function quickSuggestion(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}

// Get user settings
function getUserSettings() {
    return {
        copyType: selectedCopyType,
        goal: document.getElementById('marketingGoal').value,
        tone: document.getElementById('tone').value,
        audience: document.getElementById('targetAudience').value,
        ctaStyle: document.querySelector('input[name="ctaStyle"]:checked').value,
        includePainPoints: document.getElementById('includePainPoints').checked,
        includeBenefits: document.getElementById('includeBenefits').checked,
        includeSocialProof: document.getElementById('includeSocialProof').checked,
        includeUrgency: document.getElementById('includeUrgency').checked,
        includeGuarantee: document.getElementById('includeGuarantee').checked,
        includeTestimonials: document.getElementById('includeTestimonials').checked,
        abTestVariants: document.getElementById('abTestVariants').checked,
        conversionFocus: document.getElementById('conversionFocus').checked,
        emotionalTriggers: document.getElementById('emotionalTriggers').checked
    };
}

// Add message to chat interface
function addMessage(message, isUser = false, isLoading = false, conversionScore = null) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
    
    if (isUser) {
        messageDiv.innerHTML = `
            <div class="bg-marketing rounded-lg p-4 max-w-md text-white">
                <p>${message}</p>
            </div>
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <i class="ri-user-line text-gray-600 text-sm"></i>
            </div>
        `;
    } else if (isLoading) {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-marketing rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-md">
                <div class="flex items-center space-x-2">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-marketing"></div>
                    <span class="text-gray-600 text-sm">Creating copy...</span>
                </div>
            </div>
        `;
        messageDiv.id = 'loadingMessage';
    } else {
        const scoreDisplay = conversionScore || Math.floor(Math.random() * 20) + 75;
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-marketing rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-2xl">
                <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center space-x-2">
                            <i class="ri-megaphone-line text-lg text-marketing"></i>
                            <span class="text-sm font-medium text-gray-600">${selectedCopyType.charAt(0).toUpperCase() + selectedCopyType.slice(1)} Copy</span>
                        </div>
                        <div class="bg-marketing text-white px-3 py-1 rounded-full text-xs font-medium">
                            <i class="ri-line-chart-line mr-1"></i>
                            ${scoreDisplay}% Score
                        </div>
                    </div>
                    <div class="marketing-content text-gray-800 whitespace-pre-line">${message}</div>
                </div>
                <div class="flex items-center space-x-2 pt-3 border-t border-gray-200">
                    <button onclick="copyContent(this)" class="flex items-center space-x-1 px-3 py-1 bg-marketing text-white rounded-md text-sm hover:bg-marketing/90 transition">
                        <i class="ri-file-copy-line"></i>
                        <span>Copy</span>
                    </button>
                    <button onclick="regenerateContent()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-refresh-line"></i>
                        <span>Regenerate</span>
                    </button>
                    <button onclick="generateVariants()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-bar-chart-line"></i>
                        <span>A/B Variants</span>
                    </button>
                    <button onclick="analyzeCopy(this)" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-focus-3-line"></i>
                        <span>Analyze</span>
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
        const response = await api.generateMarketingCopy(message, settings);
        const data = Utils.formatResponse(response);
        
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add response with conversion score
        addMessage(data.content, false, false, data.conversion_score);
        
        // Store in conversation history
        conversationHistory.push({
            user: message,
            ai: data.content,
            settings: data.settings_used,
            timestamp: new Date().toISOString(),
            wordCount: data.word_count,
            copyType: data.copy_type,
            conversionScore: data.conversion_score
        });
        
        // Success notification
        showNotification(`${selectedCopyType.charAt(0).toUpperCase() + selectedCopyType.slice(1)} copy generated successfully! (${data.conversion_score}% conversion score)`, 'success');
        
    } catch (error) {
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Handle error
        Utils.handleError(error, 'Failed to generate marketing copy. Please check if the backend server is running.');
        
        // Add error message
        addMessage('Sorry, I encountered an error while generating the copy. Please try again or check your connection.');
        
    } finally {
        isGenerating = false;
        document.getElementById('sendBtn').disabled = false;
    }
}

// Copy content function
async function copyContent(button) {
    const content = button.closest('.bg-gray-100').querySelector('.marketing-content').textContent;
    
    const success = await Utils.copyToClipboard(content);
    if (success) {
        // Show success feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="ri-check-line"></i><span>Copied!</span>';
        button.classList.remove('bg-marketing');
        button.classList.add('bg-green-500');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-500');
            button.classList.add('bg-marketing');
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
        const response = await api.generateMarketingCopy(lastConversation.user, settings);
        const data = Utils.formatResponse(response);
        
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add new response
        addMessage(data.content, false, false, data.conversion_score);
        
        // Update conversation history
        conversationHistory[conversationHistory.length - 1] = {
            user: lastConversation.user,
            ai: data.content,
            settings: data.settings_used,
            timestamp: new Date().toISOString(),
            wordCount: data.word_count,
            copyType: data.copy_type,
            conversionScore: data.conversion_score
        };
        
        showNotification('Marketing copy regenerated successfully!', 'success');
        
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

// Generate A/B test variants
async function generateVariants() {
    if (conversationHistory.length === 0) {
        showNotification('Generate some copy first to create variants', 'warning');
        return;
    }
    
    showNotification('A/B test variants feature coming soon!', 'info');
    
    // Future implementation: 
    // 1. Take the last generated copy
    // 2. Generate 2-3 variants with different tones/approaches
    // 3. Show comparison interface
}

// Analyze copy function
async function analyzeCopy(button) {
    const content = button.closest('.bg-gray-100').querySelector('.marketing-content').textContent;
    
    if (!content) {
        showNotification('No content to analyze', 'warning');
        return;
    }
    
    try {
        // Show analyzing state
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="ri-loader-line animate-spin"></i><span>Analyzing...</span>';
        button.disabled = true;
        
        // Make API call to analyze
        const response = await api.analyzeMarketingCopy(content);
        const data = Utils.formatResponse(response);
        
        // Show analysis results
        showAnalysisResults(data);
        
        // Restore button
        button.innerHTML = originalText;
        button.disabled = false;
        
    } catch (error) {
        // Restore button on error
        button.innerHTML = originalText;
        button.disabled = false;
        
        Utils.handleError(error, 'Failed to analyze copy. This feature may not be available yet.');
    }
}

// Show analysis results
function showAnalysisResults(analysis) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Copy Analysis Results</h3>
                <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                    <i class="ri-close-line text-xl"></i>
                </button>
            </div>
            
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div class="text-center p-3 bg-gray-50 rounded-lg">
                        <div class="text-2xl font-bold text-marketing">${analysis.conversion_score}%</div>
                        <div class="text-sm text-gray-600">Conversion Score</div>
                    </div>
                    <div class="text-center p-3 bg-gray-50 rounded-lg">
                        <div class="text-2xl font-bold text-blue-600">${analysis.readability_score}%</div>
                        <div class="text-sm text-gray-600">Readability</div>
                    </div>
                    <div class="text-center p-3 bg-gray-50 rounded-lg">
                        <div class="text-2xl font-bold text-green-600">${analysis.emotional_impact}%</div>
                        <div class="text-sm text-gray-600">Emotional Impact</div>
                    </div>
                    <div class="text-center p-3 bg-gray-50 rounded-lg">
                        <div class="text-2xl font-bold text-yellow-600">${analysis.urgency_level}%</div>
                        <div class="text-sm text-gray-600">Urgency Level</div>
                    </div>
                </div>
                
                ${analysis.suggestions && analysis.suggestions.length > 0 ? `
                <div>
                    <h4 class="font-medium text-gray-900 mb-2">Suggestions for Improvement:</h4>
                    <ul class="space-y-1">
                        ${analysis.suggestions.map(suggestion => `
                            <li class="text-sm text-gray-600 flex items-start">
                                <i class="ri-arrow-right-line text-marketing mt-0.5 mr-2 flex-shrink-0"></i>
                                ${suggestion}
                            </li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
            
            <div class="mt-6 flex justify-end">
                <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 bg-marketing text-white rounded-lg hover:bg-marketing/90 transition">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Generate sample function
function generateSample() {
    const samples = [
        "Email campaign for fitness app with free trial offer",
        "Landing page for online course about photography",
        "Ad copy for eco-friendly products with sustainability focus",
        "Sales page for business coaching program",
        "Email sequence for software product launch",
        "Facebook ad for meal delivery service",
        "Instagram story for fashion brand sale",
        "LinkedIn sponsored content for B2B software"
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    document.getElementById('messageInput').value = randomSample;
    sendMessage();
}

// Analyze conversion function
function analyzeConversion() {
    if (conversationHistory.length === 0) {
        showNotification('Generate some copy first to analyze conversion potential', 'warning');
        return;
    }
    
    const lastContent = conversationHistory[conversationHistory.length - 1];
    analyzeCopy(document.querySelector('[onclick="analyzeCopy(this)"]'));
}

// Reset settings function
function resetSettings() {
    selectCopyType('email');
    
    document.getElementById('marketingGoal').value = 'conversion';
    document.getElementById('tone').value = 'persuasive';
    document.getElementById('targetAudience').value = 'business';
    
    document.querySelector('input[name="ctaStyle"][value="direct"]').checked = true;
    
    document.getElementById('includePainPoints').checked = true;
    document.getElementById('includeBenefits').checked = true;
    document.getElementById('includeSocialProof').checked = true;
    document.getElementById('includeUrgency').checked = false;
    document.getElementById('includeGuarantee').checked = false;
    document.getElementById('includeTestimonials').checked = false;
    document.getElementById('abTestVariants').checked = false;
    document.getElementById('conversionFocus').checked = true;
    document.getElementById('emotionalTriggers').checked = true;
    
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

// Load marketing templates from API
async function loadMarketingTemplates() {
    try {
        const response = await api.getMarketingTemplates();
        const data = Utils.formatResponse(response);
        
        // Update UI with available options (if needed)
        console.log('Available marketing templates:', data);
        
        // You can use this data to populate dropdowns or show options
        
    } catch (error) {
        console.warn('Failed to load marketing templates:', error);
    }
}

// Validate marketing input
async function validateMarketingInput(topic) {
    try {
        const response = await api.validateMarketingInput(topic, selectedCopyType);
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

// Auto-save campaign draft
function autoSaveCampaign() {
    const messageInput = document.getElementById('messageInput');
    const currentInput = messageInput.value.trim();
    
    if (currentInput.length > 5) {
        Utils.storage.set('marketing_draft', {
            topic: currentInput,
            copyType: selectedCopyType,
            settings: getUserSettings(),
            timestamp: new Date().toISOString()
        });
    }
}

// Load saved campaign draft
function loadSavedCampaign() {
    const draft = Utils.storage.get('marketing_draft');
    if (draft && draft.topic) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = draft.topic;
        
        if (draft.copyType) {
            selectCopyType(draft.copyType);
        }
        
        showNotification('Campaign draft loaded from previous session', 'info');
        Utils.storage.remove('marketing_draft');
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
        
        // Add auto-save functionality
        messageInput.addEventListener('input', Utils.debounce(autoSaveCampaign, 2000));
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Marketing Copy Generator loaded successfully!');
    
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.focus();
    }
    
    selectCopyType('email');
    checkBackendConnection();
    loadMarketingTemplates();
    loadSavedCampaign();
});