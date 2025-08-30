// Updated Blog Content Generator with Real API Integration
// File: frontend/assets/js/generators/blog.js

// Global variables
let isGenerating = false;
let conversationHistory = [];
let selectedContentType = 'article';

// Back navigation function
function goBack() {
    window.location.href = '../index.html';
}

// Content type selection
function selectContentType(type) {
    selectedContentType = type;
    
    // Remove selected class from all types
    document.querySelectorAll('.content-type-btn').forEach(btn => {
        btn.classList.remove('content-type-selected');
        btn.className = 'content-type-btn p-3 border border-gray-200 rounded-lg text-gray-700 text-xs font-medium hover:border-gray-300 flex flex-col items-center transition';
    });
    
    // Add selected class to clicked type
    const typeBtn = document.getElementById(`type-${type}`);
    typeBtn.classList.add('content-type-selected');
    typeBtn.className = 'content-type-btn p-3 border-2 border-blog bg-blog/10 rounded-lg text-blog text-xs font-medium hover:border-blog/80 flex flex-col items-center transition content-type-selected';
}

// Quick suggestion function
function quickSuggestion(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}

// Get user settings
function getUserSettings() {
    return {
        contentType: selectedContentType,
        style: document.getElementById('writingStyle').value,
        wordCount: document.getElementById('wordCount').value,
        audience: document.getElementById('targetAudience').value,
        category: document.getElementById('blogCategory').value,
        includeKeywords: document.getElementById('includeKeywords').checked,
        metaDescription: document.getElementById('metaDescription').checked,
        headingStructure: document.getElementById('headingStructure').checked,
        internalLinks: document.getElementById('internalLinks').checked,
        includeStats: document.getElementById('includeStats').checked,
        includeExamples: document.getElementById('includeExamples').checked,
        includeQuotes: document.getElementById('includeQuotes').checked,
        includeConclusion: document.getElementById('includeConclusion').checked,
        includeCTA: document.getElementById('includeCTA').checked
    };
}

// Add message to chat interface
function addMessage(message, isUser = false, isLoading = false) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
    
    if (isUser) {
        messageDiv.innerHTML = `
            <div class="bg-blog rounded-lg p-4 max-w-md text-white">
                <p>${message}</p>
            </div>
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <i class="ri-user-line text-gray-600 text-sm"></i>
            </div>
        `;
    } else if (isLoading) {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-blog rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-md">
                <div class="flex items-center space-x-2">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blog"></div>
                    <span class="text-gray-600 text-sm">Creating content...</span>
                </div>
            </div>
        `;
        messageDiv.id = 'loadingMessage';
    } else {
        const wordCount = message.split(' ').length;
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-blog rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-4 max-w-2xl">
                <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center space-x-2">
                            <i class="ri-article-line text-lg text-blog"></i>
                            <span class="text-sm font-medium text-gray-600">${selectedContentType.charAt(0).toUpperCase() + selectedContentType.slice(1)}</span>
                        </div>
                        <div class="text-xs text-gray-500">${wordCount} words</div>
                    </div>
                    <div class="blog-content text-gray-800">${formatBlogContent(message)}</div>
                </div>
                <div class="flex items-center space-x-2 pt-3 border-t border-gray-200">
                    <button onclick="copyContent(this)" class="flex items-center space-x-1 px-3 py-1 bg-blog text-white rounded-md text-sm hover:bg-blog/90 transition">
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
                    <button onclick="exportContent()" class="flex items-center space-x-1 px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50 transition">
                        <i class="ri-download-line"></i>
                        <span>Export</span>
                    </button>
                </div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    return messageDiv;
}

// Format blog content with proper HTML structure
function formatBlogContent(content) {
    // Convert markdown-style headers to HTML
    content = content.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mb-4 text-gray-900">$1</h1>');
    content = content.replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mb-3 text-gray-800">$1</h2>');
    content = content.replace(/^### (.*$)/gm, '<h3 class="text-lg font-medium mb-2 text-gray-700">$1</h3>');
    
    // Convert line breaks to paragraphs
    const paragraphs = content.split('\n\n').filter(p => p.trim());
    return paragraphs.map(p => {
        if (p.includes('<h1>') || p.includes('<h2>') || p.includes('<h3>')) {
            return p;
        }
        return `<p class="mb-4 leading-relaxed">${p}</p>`;
    }).join('');
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
    const validation = Utils.validateInput(message, 10, 200);
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
        const response = await api.generateBlogContent(message, settings);
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
            wordCount: data.word_count,
            contentType: data.content_type
        });
        
        // Auto-save to database
        if (typeof saveToHistory === 'function') {
            const saved = await saveToHistory('blog', message, data.content, 'gpt2', settings);
            if (saved) {
                console.log('Blog content saved to history');
            }
        }
        
        // Success notification
        showNotification(`${selectedContentType.charAt(0).toUpperCase() + selectedContentType.slice(1)} content generated successfully!`, 'success');
        
    } catch (error) {
        // Remove loading message
        const loadingElement = document.getElementById('loadingMessage');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Handle error
        Utils.handleError(error, 'Failed to generate blog content. Please check if the backend server is running.');
        
        // Add error message
        addMessage('Sorry, I encountered an error while generating the content. Please try again or check your connection.');
        
    } finally {
        isGenerating = false;
        document.getElementById('sendBtn').disabled = false;
    }
}

// Copy content function
async function copyContent(button) {
    const content = button.closest('.bg-gray-100').querySelector('.blog-content').textContent;
    
    const success = await Utils.copyToClipboard(content);
    if (success) {
        // Show success feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="ri-check-line"></i><span>Copied!</span>';
        button.classList.remove('bg-blog');
        button.classList.add('bg-green-500');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-500');
            button.classList.add('bg-blog');
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
        const response = await api.generateBlogContent(lastConversation.user, settings);
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
            wordCount: data.word_count,
            contentType: data.content_type
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
    showNotification('Content improvement suggestions feature coming soon!', 'info');
}

// Export content function
async function exportContent() {
    if (conversationHistory.length === 0) {
        showNotification('No content to export', 'warning');
        return;
    }
    
    try {
        const lastContent = conversationHistory[conversationHistory.length - 1];
        const filename = `blog-content-${Date.now()}.txt`;
        
        // Create file content with metadata
        const fileContent = `Blog Content Export
Generated: ${Utils.formatDate(lastContent.timestamp)}
Topic: ${lastContent.user}
Content Type: ${lastContent.contentType}
Word Count: ${lastContent.wordCount}

---

${lastContent.ai}`;
        
        // Create and download file
        const blob = new Blob([fileContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Content exported successfully!', 'success');
        
    } catch (error) {
        Utils.handleError(error, 'Failed to export content');
    }
}

// Generate sample function
function generateSample() {
    const samples = [
        "The ultimate guide to remote work productivity in 2024",
        "How artificial intelligence is transforming healthcare",
        "Sustainable business practices for small companies",
        "Digital marketing trends every entrepreneur should know",
        "The psychology of effective team leadership",
        "Complete beginner's guide to cryptocurrency investing",
        "Future of renewable energy technologies",
        "Building resilient supply chains in modern business"
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    document.getElementById('messageInput').value = randomSample;
    sendMessage();
}

// Generate outline function
async function generateOutline() {
    const currentInput = document.getElementById('messageInput').value.trim();
    if (!currentInput) {
        showNotification('Please enter a topic first', 'warning');
        return;
    }
    
    // Set content type to outline
    selectContentType('outline');
    
    // Generate with outline settings
    await sendMessage();
}

// Reset settings function
function resetSettings() {
    // Reset content type to article
    selectContentType('article');
    
    // Reset dropdowns
    document.getElementById('writingStyle').value = 'informative';
    document.getElementById('wordCount').value = '500';
    document.getElementById('targetAudience').value = 'general';
    document.getElementById('blogCategory').value = 'technology';
    
    // Reset checkboxes
    document.getElementById('includeKeywords').checked = true;
    document.getElementById('metaDescription').checked = true;
    document.getElementById('headingStructure').checked = false;
    document.getElementById('internalLinks').checked = false;
    document.getElementById('includeStats').checked = true;
    document.getElementById('includeExamples').checked = true;
    document.getElementById('includeQuotes').checked = false;
    document.getElementById('includeConclusion').checked = true;
    document.getElementById('includeCTA').checked = false;
    
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
async function loadBlogTemplates() {
    try {
        const response = await api.getBlogTemplates();
        const data = Utils.formatResponse(response);
        
        // Update UI with available options (if needed)
        console.log('Available blog templates:', data);
        
        // You can use this data to populate dropdowns or show options
        
    } catch (error) {
        console.warn('Failed to load blog templates:', error);
    }
}

// Validate input before sending
async function validateBlogInput(topic) {
    try {
        const response = await api.validateBlogInput(topic);
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

// Update word count indicator
function updateWordCountIndicator() {
    const messageInput = document.getElementById('messageInput');
    const selectedWordCount = document.getElementById('wordCount').value;
    
    // You can add a visual indicator showing target word count
    // This is optional UI enhancement
}

// Auto-save draft functionality
function autoSaveDraft() {
    const messageInput = document.getElementById('messageInput');
    const currentInput = messageInput.value.trim();
    
    if (currentInput.length > 10) {
        Utils.storage.set('blog_draft', {
            topic: currentInput,
            settings: getUserSettings(),
            timestamp: new Date().toISOString()
        });
    }
}

// Load saved draft
function loadSavedDraft() {
    const draft = Utils.storage.get('blog_draft');
    if (draft && draft.topic) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = draft.topic;
        
        // Show notification about loaded draft
        showNotification('Draft loaded from previous session', 'info');
        
        // Clear the draft after loading
        Utils.storage.remove('blog_draft');
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
        messageInput.addEventListener('input', Utils.debounce(autoSaveDraft, 2000));
        
        // Add word count update
        messageInput.addEventListener('input', updateWordCountIndicator);
    }
    
    // Add change listeners for settings
    document.getElementById('wordCount').addEventListener('change', updateWordCountIndicator);
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Blog Content Generator loaded successfully!');
    
    // Focus on input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.focus();
    }
    
    // Set default content type
    selectContentType('article');
    
    // Check backend connection
    checkBackendConnection();
    
    // Load templates
    loadBlogTemplates();
    
    // Load saved draft if available
    loadSavedDraft();
});