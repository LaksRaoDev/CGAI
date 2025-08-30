// History Page JavaScript
// File: assets/js/history.js

let currentPage = 1;
let totalPages = 1;
let currentEditId = null;

// API Base URL
const API_BASE = 'http://localhost:5000/api/v1';

// Get user token
function getToken() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.token || '';
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!checkAuth()) {
        return;
    }
    
    // Load initial data
    loadHistory();
    loadStats();
    
    // Setup event listeners
    document.getElementById('contentTypeFilter').addEventListener('change', () => {
        currentPage = 1;
        loadHistory();
    });
    
    document.getElementById('searchInput').addEventListener('input', debounce(() => {
        currentPage = 1;
        loadHistory();
    }, 500));
});

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/history/stats`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load stats');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update stat cards
            document.getElementById('totalCount').textContent = data.stats.total || 0;
            document.getElementById('productCount').textContent = data.stats.by_type.product || 0;
            document.getElementById('blogCount').textContent = data.stats.by_type.blog || 0;
            document.getElementById('socialCount').textContent = data.stats.by_type.social || 0;
            document.getElementById('marketingCount').textContent = data.stats.by_type.marketing || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load history
async function loadHistory() {
    const historyList = document.getElementById('historyList');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const pagination = document.getElementById('pagination');
    
    // Show loading state
    historyList.innerHTML = '';
    loadingState.classList.remove('hidden');
    emptyState.classList.add('hidden');
    pagination.classList.add('hidden');
    
    try {
        // Build query parameters
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 10
        });
        
        const contentType = document.getElementById('contentTypeFilter').value;
        if (contentType) {
            params.append('content_type', contentType);
        }
        
        const search = document.getElementById('searchInput').value;
        if (search) {
            params.append('search', search);
        }
        
        const response = await fetch(`${API_BASE}/history/list?${params}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        
        const data = await response.json();
        
        loadingState.classList.add('hidden');
        
        if (data.success) {
            if (data.history.length === 0) {
                emptyState.classList.remove('hidden');
            } else {
                renderHistoryItems(data.history);
                renderPagination(data.pagination);
            }
        }
    } catch (error) {
        console.error('Error loading history:', error);
        loadingState.classList.add('hidden');
        showNotification('Failed to load history', 'error');
    }
}

// Render history items
function renderHistoryItems(items) {
    const historyList = document.getElementById('historyList');
    
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow p-6 hover:shadow-lg transition';
        
        const typeIcon = getTypeIcon(item.content_type);
        const typeColor = getTypeColor(item.content_type);
        
        card.innerHTML = `
            <div class="flex items-start justify-between mb-4">
                <div class="flex items-start space-x-4">
                    <div class="w-12 h-12 ${typeColor.bg} rounded-lg flex items-center justify-center flex-shrink-0">
                        <i class="${typeIcon} ${typeColor.text} text-xl"></i>
                    </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-gray-900 mb-1">${formatContentType(item.content_type)}</h3>
                        <p class="text-sm text-gray-500">${formatDate(item.created_at)}</p>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <button onclick="copyContent(${item.id})" class="text-gray-400 hover:text-gray-600 transition" title="Copy">
                        <i class="ri-file-copy-line text-xl"></i>
                    </button>
                    <button onclick="openEditModal(${item.id})" class="text-gray-400 hover:text-blue-600 transition" title="Edit">
                        <i class="ri-edit-line text-xl"></i>
                    </button>
                    <button onclick="deleteHistory(${item.id})" class="text-gray-400 hover:text-red-600 transition" title="Delete">
                        <i class="ri-delete-bin-line text-xl"></i>
                    </button>
                </div>
            </div>
            
            <div class="space-y-3">
                <div>
                    <p class="text-sm font-medium text-gray-700 mb-1">Prompt:</p>
                    <p class="text-sm text-gray-600 bg-gray-50 rounded p-3">${escapeHtml(item.prompt)}</p>
                </div>
                
                <div>
                    <p class="text-sm font-medium text-gray-700 mb-1">Generated Content:</p>
                    <div class="text-sm text-gray-600 bg-gray-50 rounded p-3 max-h-32 overflow-y-auto" id="content-${item.id}">
                        ${escapeHtml(item.generated_content)}
                    </div>
                </div>
                
                <div class="flex items-center justify-between pt-3 border-t border-gray-100">
                    <span class="text-xs text-gray-500">Model: ${item.model_used}</span>
                    ${item.updated_at !== item.created_at ? 
                        `<span class="text-xs text-gray-500">Updated: ${formatDate(item.updated_at)}</span>` : 
                        ''}
                </div>
            </div>
        `;
        
        historyList.appendChild(card);
    });
}

// Render pagination
function renderPagination(paginationData) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (paginationData.pages <= 1) {
        pagination.classList.add('hidden');
        return;
    }
    
    pagination.classList.remove('hidden');
    
    // Previous button
    if (paginationData.has_prev) {
        const prevBtn = document.createElement('button');
        prevBtn.className = 'px-3 py-1 text-gray-500 bg-white border border-gray-300 rounded hover:bg-gray-50 transition';
        prevBtn.innerHTML = '<i class="ri-arrow-left-s-line"></i>';
        prevBtn.onclick = () => {
            currentPage--;
            loadHistory();
        };
        pagination.appendChild(prevBtn);
    }
    
    // Page numbers
    for (let i = 1; i <= paginationData.pages; i++) {
        if (i === 1 || i === paginationData.pages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageBtn = document.createElement('button');
            pageBtn.className = i === currentPage ? 
                'px-3 py-1 bg-primary text-white rounded' : 
                'px-3 py-1 text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition';
            pageBtn.textContent = i;
            pageBtn.onclick = () => {
                currentPage = i;
                loadHistory();
            };
            pagination.appendChild(pageBtn);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const dots = document.createElement('span');
            dots.className = 'px-2 text-gray-500';
            dots.textContent = '...';
            pagination.appendChild(dots);
        }
    }
    
    // Next button
    if (paginationData.has_next) {
        const nextBtn = document.createElement('button');
        nextBtn.className = 'px-3 py-1 text-gray-500 bg-white border border-gray-300 rounded hover:bg-gray-50 transition';
        nextBtn.innerHTML = '<i class="ri-arrow-right-s-line"></i>';
        nextBtn.onclick = () => {
            currentPage++;
            loadHistory();
        };
        pagination.appendChild(nextBtn);
    }
}

// Open edit modal
async function openEditModal(id) {
    try {
        const response = await fetch(`${API_BASE}/history/${id}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load content');
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentEditId = id;
            document.getElementById('editPrompt').value = data.history.prompt;
            document.getElementById('editContent').value = data.history.generated_content;
            document.getElementById('editModal').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading content:', error);
        showNotification('Failed to load content', 'error');
    }
}

// Close edit modal
function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
    currentEditId = null;
}

// Save edit
async function saveEdit() {
    if (!currentEditId) return;
    
    const prompt = document.getElementById('editPrompt').value;
    const content = document.getElementById('editContent').value;
    
    try {
        const response = await fetch(`${API_BASE}/history/${currentEditId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                prompt: prompt,
                generated_content: content
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update content');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Content updated successfully', 'success');
            closeEditModal();
            loadHistory();
        }
    } catch (error) {
        console.error('Error updating content:', error);
        showNotification('Failed to update content', 'error');
    }
}

// Delete history item
async function deleteHistory(id) {
    if (!confirm('Are you sure you want to delete this content?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/history/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete content');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Content deleted successfully', 'success');
            loadHistory();
            loadStats();
        }
    } catch (error) {
        console.error('Error deleting content:', error);
        showNotification('Failed to delete content', 'error');
    }
}

// Copy content to clipboard
async function copyContent(id) {
    const contentElement = document.getElementById(`content-${id}`);
    if (contentElement) {
        const text = contentElement.textContent;
        try {
            await navigator.clipboard.writeText(text);
            showNotification('Content copied to clipboard', 'success');
        } catch (error) {
            console.error('Error copying content:', error);
            showNotification('Failed to copy content', 'error');
        }
    }
}

// Refresh history
function refreshHistory() {
    loadHistory();
    loadStats();
    showNotification('History refreshed', 'success');
}

// Helper functions
function getTypeIcon(type) {
    const icons = {
        'product': 'ri-shopping-bag-line',
        'social': 'ri-smartphone-line',
        'blog': 'ri-article-line',
        'marketing': 'ri-megaphone-line'
    };
    return icons[type] || 'ri-file-text-line';
}

function getTypeColor(type) {
    const colors = {
        'product': { bg: 'bg-blue-100', text: 'text-blue-600' },
        'social': { bg: 'bg-green-100', text: 'text-green-600' },
        'blog': { bg: 'bg-purple-100', text: 'text-purple-600' },
        'marketing': { bg: 'bg-orange-100', text: 'text-orange-600' }
    };
    return colors[type] || { bg: 'bg-gray-100', text: 'text-gray-600' };
}

function formatContentType(type) {
    const types = {
        'product': 'Product Description',
        'social': 'Social Media Post',
        'blog': 'Blog Content',
        'marketing': 'Marketing Copy'
    };
    return types[type] || 'Content';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Go back function
function goBack() {
    window.location.href = '../index.html';
}