// AI Model Management for ContentAI Pro
// File: assets/js/models.js

class ModelManager {
    constructor() {
        this.apiBase = 'http://localhost:5000/api/v1';
        this.currentModel = null;
        this.availableModels = [];
        this.isLoading = false;
        
        this.init();
    }

    async init() {
        await this.loadAvailableModels();
        await this.getCurrentModel();
        this.createModelSwitcher();
    }

    async loadAvailableModels() {
        try {
            const response = await fetch(`${this.apiBase}/models/list`);
            const data = await response.json();
            
            if (data.success) {
                this.availableModels = data.data.models;
                console.log('✅ Available models loaded:', this.availableModels.length);
            }
        } catch (error) {
            console.error('❌ Failed to load models:', error);
            this.showNotification('Failed to load AI models', 'error');
        }
    }

    async getCurrentModel() {
        try {
            const response = await fetch(`${this.apiBase}/models/current`);
            const data = await response.json();
            
            if (data.success) {
                this.currentModel = data.data;
                console.log('✅ Current model:', this.currentModel.name);
            }
        } catch (error) {
            console.error('❌ Failed to get current model:', error);
        }
    }

    createModelSwitcher() {
        // Create model indicator in header
        this.createModelIndicator();
        
        // Create model switcher button
        const buttonHTML = `
            <button id="modelSwitcherBtn" onclick="modelManager.openModal()" class="fixed bottom-6 right-6 bg-gradient-to-r from-primary to-accent text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 z-40">
                <div class="flex items-center space-x-2">
                    <i class="ri-cpu-line text-xl"></i>
                    <span class="hidden md:inline font-medium">AI Models</span>
                </div>
            </button>
        `;

        document.body.insertAdjacentHTML('beforeend', buttonHTML);
    }

    createModelIndicator() {
        // Add model indicator to all pages
        const headers = document.querySelectorAll('header .flex.justify-between');
        headers.forEach(header => {
            const rightSection = header.querySelector('.flex.items-center.space-x-4');
            if (rightSection) {
                const indicator = document.createElement('div');
                indicator.id = 'currentModelIndicator';
                indicator.className = 'hidden sm:flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg cursor-pointer hover:bg-gray-200 transition';
                indicator.onclick = () => this.openModal();
                rightSection.insertBefore(indicator, rightSection.firstChild);
                this.updateModelIndicator();
            }
        });
    }

    updateModelIndicator() {
        const indicator = document.getElementById('currentModelIndicator');
        if (indicator && this.currentModel) {
            indicator.innerHTML = `
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">${this.currentModel.name}</span>
                <i class="ri-arrow-down-s-line text-gray-500"></i>
            `;
        }
    }

    openModal() {
        this.createModalIfNotExists();
        const modal = document.getElementById('modelSwitcherModal');
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            this.populateModal();
        }
    }

    createModalIfNotExists() {
        if (document.getElementById('modelSwitcherModal')) return;

        const modalHTML = `
            <div id="modelSwitcherModal" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-50">
                <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
                    <!-- Header -->
                    <div class="bg-gradient-to-r from-primary to-accent p-6 text-white">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-3">
                                <div class="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                                    <i class="ri-cpu-line text-2xl"></i>
                                </div>
                                <div>
                                    <h2 class="text-2xl font-bold">AI Model Manager</h2>
                                    <p class="text-white text-opacity-90">Choose the perfect AI model for your content</p>
                                </div>
                            </div>
                            <button onclick="modelManager.closeModal()" class="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center hover:bg-opacity-30 transition">
                                <i class="ri-close-line text-xl"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Content -->
                    <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                        <!-- Current Model Info -->
                        <div id="currentModelInfo" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                            <div class="flex items-center space-x-3 mb-3">
                                <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                                    <i class="ri-star-line text-white text-sm"></i>
                                </div>
                                <h3 class="text-lg font-semibold text-gray-900">Currently Active Model</h3>
                            </div>
                            <div id="currentModelDetails">
                                <!-- Will be populated dynamically -->
                            </div>
                        </div>

                        <!-- Model Grid -->
                        <h3 class="text-xl font-bold text-gray-900 mb-4">🤖 Available AI Models</h3>
                        <div id="modelsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                            <!-- Models will be populated here -->
                        </div>

                        <!-- Quick Actions -->
                        <div class="border-t pt-6">
                            <h3 class="text-xl font-bold text-gray-900 mb-4">⚡ Quick Actions</h3>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <button onclick="modelManager.switchToRecommended('product')" class="p-4 border border-gray-200 rounded-lg hover:border-primary hover:bg-primary/5 transition">
                                    <i class="ri-shopping-bag-line text-2xl text-blue-600 mb-2"></i>
                                    <div class="font-semibold">Best for Products</div>
                                    <div class="text-sm text-gray-500">Switch to optimal model for product descriptions</div>
                                </button>
                                <button onclick="modelManager.switchToRecommended('social')" class="p-4 border border-gray-200 rounded-lg hover:border-primary hover:bg-primary/5 transition">
                                    <i class="ri-smartphone-line text-2xl text-green-600 mb-2"></i>
                                    <div class="font-semibold">Best for Social</div>
                                    <div class="text-sm text-gray-500">Switch to optimal model for social media</div>
                                </button>
                                <button onclick="modelManager.switchToRecommended('blog')" class="p-4 border border-gray-200 rounded-lg hover:border-primary hover:bg-primary/5 transition">
                                    <i class="ri-article-line text-2xl text-purple-600 mb-2"></i>
                                    <div class="font-semibold">Best for Blogs</div>
                                    <div class="text-sm text-gray-500">Switch to optimal model for blog content</div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    populateModal() {
        this.updateCurrentModelInfo();
        this.updateModelsGrid();
    }

    updateCurrentModelInfo() {
        const container = document.getElementById('currentModelDetails');
        if (!container || !this.currentModel) return;

        container.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <h4 class="font-bold text-gray-900 mb-2">${this.currentModel.name}</h4>
                    <p class="text-gray-600 text-sm mb-3">${this.currentModel.description}</p>
                    <div class="flex flex-wrap gap-2">
                        ${this.currentModel.strengths?.map(strength => 
                            `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">${strength}</span>`
                        ).join('') || ''}
                    </div>
                </div>
                <div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="text-center p-3 bg-white rounded-lg border">
                            <div class="text-2xl font-bold text-gray-900">${this.currentModel.quality}</div>
                            <div class="text-sm text-gray-500">Quality</div>
                        </div>
                        <div class="text-center p-3 bg-white rounded-lg border">
                            <div class="text-2xl font-bold text-gray-900">${this.currentModel.speed}</div>
                            <div class="text-sm text-gray-500">Speed</div>
                        </div>
                        <div class="text-center p-3 bg-white rounded-lg border">
                            <div class="text-2xl font-bold text-gray-900">${this.currentModel.cost}</div>
                            <div class="text-sm text-gray-500">Cost</div>
                        </div>
                        <div class="text-center p-3 bg-white rounded-lg border">
                            <div class="text-2xl font-bold text-gray-900">${this.currentModel.stats?.uses || 0}</div>
                            <div class="text-sm text-gray-500">Uses</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateModelsGrid() {
        const container = document.getElementById('modelsGrid');
        if (!container) return;

        container.innerHTML = this.availableModels.map(model => `
            <div class="model-card bg-white border-2 ${model.current ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-gray-200'} rounded-xl p-5 hover:shadow-lg hover:border-primary/50 transition-all cursor-pointer group">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 ${this.getModelIcon(model.key)} rounded-xl flex items-center justify-center">
                            <i class="ri-brain-line text-white text-lg"></i>
                        </div>
                        <div>
                            <h4 class="font-bold text-gray-900">${model.name}</h4>
                            <p class="text-xs text-gray-500 uppercase tracking-wide">${model.key}</p>
                        </div>
                    </div>
                    ${model.current ? 
                        '<div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center"><i class="ri-check-line text-white"></i></div>' : 
                        '<div class="w-8 h-8 border-2 border-gray-200 rounded-full group-hover:border-primary transition-colors"></div>'
                    }
                </div>
                
                <p class="text-gray-600 text-sm mb-4 h-10 overflow-hidden">${model.description}</p>
                
                <!-- Quality indicators -->
                <div class="grid grid-cols-3 gap-3 mb-4">
                    <div class="text-center">
                        <div class="text-xs text-gray-500 mb-1">Quality</div>
                        <div class="flex items-center justify-center">
                            ${this.getStarRating(model.quality)}
                        </div>
                    </div>
                    <div class="text-center">
                        <div class="text-xs text-gray-500 mb-1">Speed</div>
                        <div class="flex items-center justify-center">
                            ${this.getSpeedIndicator(model.speed)}
                        </div>
                    </div>
                    <div class="text-center">
                        <div class="text-xs text-gray-500 mb-1">Cost</div>
                        <div class="text-xs font-semibold ${model.cost === 'Free' ? 'text-green-600' : 'text-blue-600'}">${model.cost}</div>
                    </div>
                </div>
                
                <!-- Status and usage -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-2">
                        <div class="w-2 h-2 rounded-full ${model.available ? 'bg-green-500' : 'bg-red-500'}"></div>
                        <span class="text-xs ${model.available ? 'text-green-600' : 'text-red-600'} font-medium">
                            ${model.available ? 'Ready' : 'Unavailable'}
                        </span>
                    </div>
                    <div class="text-xs text-gray-500">
                        Used ${model.stats?.uses || 0} times
                    </div>
                </div>
                
                <!-- Action button -->
                ${model.current ? 
                    '<div class="w-full bg-green-100 text-green-800 py-3 px-4 rounded-lg text-center font-semibold text-sm flex items-center justify-center space-x-2"><i class="ri-check-line"></i><span>Currently Active</span></div>' :
                    (model.available ? 
                        `<button onclick="modelManager.switchModel('${model.key}')" class="w-full bg-primary text-white py-3 px-4 rounded-lg font-semibold text-sm hover:bg-primary/90 transition flex items-center justify-center space-x-2">
                            <i class="ri-refresh-line"></i>
                            <span>Switch to ${model.name}</span>
                        </button>` :
                        '<div class="w-full bg-gray-100 text-gray-500 py-3 px-4 rounded-lg text-center font-semibold text-sm">Not Available</div>'
                    )
                }
            </div>
        `).join('');
    }

    getModelIcon(modelKey) {
        const icons = {
            'gemini': 'bg-gradient-to-r from-blue-500 to-blue-600',
            'gpt2': 'bg-gradient-to-r from-green-500 to-green-600',
            'gpt2-medium': 'bg-gradient-to-r from-green-600 to-green-700',
            'distilgpt2': 'bg-gradient-to-r from-green-400 to-green-500',
            't5-small': 'bg-gradient-to-r from-purple-500 to-purple-600',
            'bart-base': 'bg-gradient-to-r from-orange-500 to-orange-600'
        };
        return icons[modelKey] || 'bg-gradient-to-r from-gray-500 to-gray-600';
    }

    getStarRating(quality) {
        const ratings = {
            'Excellent': 5,
            'Very Good': 4,
            'Good': 3,
            'Fair': 2
        };
        const rating = ratings[quality] || 1;
        return Array.from({length: 5}, (_, i) => 
            `<i class="ri-star-${i < rating ? 'fill' : 'line'} text-yellow-400 text-xs"></i>`
        ).join('');
    }

    getSpeedIndicator(speed) {
        const indicators = {
            'Very Fast': '<i class="ri-flashlight-fill text-green-500"></i>',
            'Fast': '<i class="ri-flashlight-fill text-blue-500"></i>',
            'Medium': '<i class="ri-flashlight-fill text-yellow-500"></i>',
            'Slower': '<i class="ri-flashlight-fill text-orange-500"></i>'
        };
        return indicators[speed] || '<i class="ri-flashlight-line text-gray-400"></i>';
    }

    async switchModel(modelKey) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showNotification('Switching AI model...', 'info');
        
        try {
            const response = await fetch(`${this.apiBase}/models/switch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ model: modelKey })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`✅ Switched to ${data.model_info.name}!`, 'success');
                await this.getCurrentModel();
                this.populateModal();
                this.updateModelIndicator();
            } else {
                this.showNotification(`❌ Failed to switch model: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('❌ Model switch failed:', error);
            this.showNotification('❌ Failed to switch model. Please try again.', 'error');
        } finally {
            this.isLoading = false;
        }
    }

    async switchToRecommended(contentType) {
        try {
            const recommendations = await this.getRecommendations(contentType);
            if (recommendations.length > 0) {
                const bestModel = recommendations[0];
                await this.switchModel(bestModel.model);
                this.showNotification(`🎯 Switched to ${bestModel.model} - ${bestModel.reason}`, 'success');
            }
        } catch (error) {
            this.showNotification('❌ Failed to get recommendations', 'error');
        }
    }

    closeModal() {
        const modal = document.getElementById('modelSwitcherModal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    }

    showNotification(message, type = 'info') {
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    async getRecommendations(contentType, requirements = {}) {
        try {
            const response = await fetch(`${this.apiBase}/models/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content_type: contentType,
                    requirements: requirements
                })
            });
            
            const data = await response.json();
            if (data.success) {
                return data.data.recommendations;
            }
        } catch (error) {
            console.error('❌ Failed to get recommendations:', error);
        }
        return [];
    }

    async generateContent(prompt, contentType, settings = {}) {
        try {
            const response = await fetch(`${this.apiBase}/models/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    content_type: contentType,
                    settings: settings
                })
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('❌ Content generation failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Initialize model manager when DOM is loaded
let modelManager;
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for auth to initialize first
    setTimeout(() => {
        modelManager = new ModelManager();
    }, 1000);
});

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModelManager;
}
