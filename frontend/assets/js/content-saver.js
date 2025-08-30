// Content Saving Utility
// File: assets/js/content-saver.js

// API Base URL
const CONTENT_API_BASE = 'http://localhost:5000/api/v1';

// Save generated content to history
async function saveToHistory(contentType, prompt, generatedContent, modelUsed = 'gpt2', parameters = {}) {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!user.token) {
        console.log('User not authenticated, skipping save');
        return false;
    }
    
    try {
        const response = await fetch(`${CONTENT_API_BASE}/history/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${user.token}`
            },
            body: JSON.stringify({
                content_type: contentType,
                prompt: prompt,
                generated_content: generatedContent,
                model_used: modelUsed,
                parameters: parameters
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Content saved to history:', data.history_id);
            return true;
        } else {
            console.error('Failed to save content:', data.message);
            return false;
        }
    } catch (error) {
        console.error('Error saving content to history:', error);
        return false;
    }
}

// Auto-save wrapper for generator functions
function wrapGeneratorFunction(originalFunction, contentType) {
    return async function(...args) {
        // Call the original generator function
        const result = await originalFunction.apply(this, args);
        
        // Extract prompt and generated content from the result
        // This assumes the generator function updates the DOM
        // We'll need to extract the values from the DOM elements
        
        setTimeout(() => {
            // Get prompt from input fields (adjust selectors based on actual page structure)
            let prompt = '';
            const promptElements = document.querySelectorAll('input[type="text"], textarea');
            promptElements.forEach(el => {
                if (el.value && !el.id.includes('result')) {
                    prompt += el.value + ' ';
                }
            });
            
            // Get generated content from result area
            let generatedContent = '';
            const resultElement = document.getElementById('result') || 
                                 document.getElementById('generatedContent') ||
                                 document.querySelector('.result-area');
            
            if (resultElement) {
                generatedContent = resultElement.textContent || resultElement.value || '';
            }
            
            // Save if we have both prompt and content
            if (prompt.trim() && generatedContent.trim()) {
                saveToHistory(contentType, prompt.trim(), generatedContent.trim());
            }
        }, 500); // Small delay to ensure DOM is updated
        
        return result;
    };
}

// Initialize auto-save for current page
function initializeAutoSave() {
    // Detect which generator page we're on
    const path = window.location.pathname;
    let contentType = '';
    
    if (path.includes('product-generator')) {
        contentType = 'product';
    } else if (path.includes('social-media')) {
        contentType = 'social';
    } else if (path.includes('blog-content')) {
        contentType = 'blog';
    } else if (path.includes('marketing-copy')) {
        contentType = 'marketing';
    }
    
    if (contentType) {
        console.log(`Auto-save initialized for ${contentType} content`);
        
        // Hook into the generate button click event
        document.addEventListener('DOMContentLoaded', () => {
            const generateButtons = document.querySelectorAll('button');
            generateButtons.forEach(button => {
                if (button.textContent.includes('Generate') || 
                    button.onclick && button.onclick.toString().includes('generate')) {
                    
                    const originalOnclick = button.onclick;
                    button.onclick = function(event) {
                        // Call original function
                        if (originalOnclick) {
                            originalOnclick.call(this, event);
                        }
                        
                        // Auto-save after generation
                        setTimeout(() => {
                            const prompt = collectPromptData();
                            const content = collectGeneratedContent();
                            
                            if (prompt && content) {
                                saveToHistory(contentType, prompt, content);
                            }
                        }, 2000); // Wait for generation to complete
                    };
                }
            });
        });
    }
}

// Helper function to collect prompt data from the page
function collectPromptData() {
    let prompt = '';
    
    // Collect from all input fields
    const inputs = document.querySelectorAll('input[type="text"]:not([readonly]), textarea:not([readonly])');
    inputs.forEach(input => {
        if (input.value && !input.id.includes('result') && !input.id.includes('generated')) {
            const label = document.querySelector(`label[for="${input.id}"]`);
            if (label) {
                prompt += `${label.textContent}: ${input.value}\n`;
            } else {
                prompt += `${input.value}\n`;
            }
        }
    });
    
    // Collect from select dropdowns
    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        if (select.value) {
            const label = document.querySelector(`label[for="${select.id}"]`);
            if (label) {
                prompt += `${label.textContent}: ${select.value}\n`;
            }
        }
    });
    
    return prompt.trim();
}

// Helper function to collect generated content
function collectGeneratedContent() {
    // Try different possible result containers
    const resultContainers = [
        document.getElementById('result'),
        document.getElementById('generatedContent'),
        document.getElementById('output'),
        document.querySelector('.result-area'),
        document.querySelector('.generated-content'),
        document.querySelector('[id*="result"]'),
        document.querySelector('[id*="generated"]')
    ];
    
    for (const container of resultContainers) {
        if (container && container.textContent) {
            return container.textContent.trim();
        } else if (container && container.value) {
            return container.value.trim();
        }
    }
    
    return '';
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAutoSave);
} else {
    initializeAutoSave();
}