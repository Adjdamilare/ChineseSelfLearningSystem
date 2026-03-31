/**
 * Stroke Order Search JavaScript
 * Uses Hanzi Writer CDN for accurate stroke order animations
 */

// Load Hanzi Writer from CDN
const HANZI_WRITER_CDN = 'https://cdn.jsdelivr.net/npm/hanzi-writer@3.5/dist/hanzi-writer.min.js';

// DOM Elements
const searchInput = document.getElementById('stroke-search-input');
const searchBtn = document.getElementById('search-btn');
const clearBtn = document.getElementById('clear-search');
const loadingIndicator = document.getElementById('loading-indicator');
const resultsSection = document.getElementById('results-section');
const characterGrid = document.getElementById('character-grid');
const resultsCount = document.getElementById('results-count');
const noResults = document.getElementById('no-results');
const welcomeMessage = document.getElementById('welcome-message');

// Track all Hanzi Writer instances for cleanup
let writerInstances = [];

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load Hanzi Writer dynamically
    loadHanziWriter().then(() => {
        console.log('Hanzi Writer loaded successfully');
    }).catch(err => {
        console.error('Failed to load Hanzi Writer:', err);
        showToast('Failed to load stroke animation library', 'error');
    });

    searchBtn.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    clearBtn.addEventListener('click', clearSearch);
    
    searchInput.addEventListener('input', function() {
        clearBtn.style.display = this.value.length > 0 ? 'flex' : 'none';
    });
    
    document.querySelectorAll('.hint-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            searchInput.value = this.getAttribute('data-value');
            clearBtn.style.display = 'flex';
            performSearch();
        });
    });
});

/**
 * Load Hanzi Writer from CDN dynamically
 */
function loadHanziWriter() {
    return new Promise((resolve, reject) => {
        if (typeof HanziWriter !== 'undefined') {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = HANZI_WRITER_CDN;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Perform the search
 */
async function performSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        showToast('Please enter Chinese characters', 'error');
        return;
    }
    
    // Clean up existing writers
    cleanupWriters();
    
    showLoading();
    hideResults();
    hideWelcome();
    hideNoResults();
    
    try {
        const response = await fetch(`/api/stroke-order/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (response.ok && data.results && data.results.length > 0) {
            displayResults(data.results);
        } else {
            showNoResults();
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed. Please try again.', 'error');
        hideLoading();
        showWelcome();
    }
}

/**
 * Display search results with Hanzi Writer animations
 */
function displayResults(results) {
    hideLoading();
    showResults();
    
    resultsCount.textContent = `${results.length} word${results.length !== 1 ? 's' : ''} found`;
    characterGrid.innerHTML = '';
    
    results.forEach((result, index) => {
        const card = createWordCard(result, index);
        characterGrid.appendChild(card);
    });
    
    // Initialize Hanzi Writer for each character after DOM is updated
    requestAnimationFrame(() => {
        results.forEach((result, wordIndex) => {
            result.characters.forEach((charData, charIndex) => {
                initHanziWriter(charData.character, wordIndex, charIndex);
            });
        });
    });
}

/**
 * Initialize Hanzi Writer for a single character
 */
function initHanziWriter(character, wordIndex, charIndex) {
    const containerId = `hanzi-container-${wordIndex}-${charIndex}`;
    const container = document.getElementById(containerId);
    
    if (!container || typeof HanziWriter === 'undefined') {
        console.warn(`Cannot initialize writer for ${character}`);
        return;
    }
    
    const writer = HanziWriter.create(containerId, character, {
        width: 150,
        height: 150,
        padding: 5,
        showOutline: true,
        strokeAnimationSpeed: 1,
        delayBetweenStrokes: 300,
        radicalColor: '#3498db',
        strokeColor: '#2c3e50',
        outlineColor: '#e0e0e0',
        drawingWidth: 4,
        drawingColor: 'rgba(0, 113, 227, 0.7)',
    });
    
    writerInstances.push({
        writer,
        character,
        wordIndex,
        charIndex
    });
    
    // Auto-animate first character of first word
    if (wordIndex === 0 && charIndex === 0) {
        setTimeout(() => {
            writer.animateCharacter();
        }, 500);
    }
}

/**
 * Create a word card with Hanzi Writer containers
 */
function createWordCard(result, index) {
    const card = document.createElement('div');
    card.className = 'character-card fade-in';
    card.style.animationDelay = `${index * 0.1}s`;
    
    // Build character containers HTML
    let charactersHtml = '';
    result.characters.forEach((char, charIndex) => {
        charactersHtml += `
            <div class="character-animation-box">
                <div class="character-display">${char.character}</div>
                <div id="hanzi-container-${index}-${charIndex}" class="hanzi-writer-container"></div>
                <div class="animation-controls">
                    <button class="anim-btn play-btn" data-word="${index}" data-char="${charIndex}" title="Play Animation">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="anim-btn quiz-btn" data-word="${index}" data-char="${charIndex}" title="Quiz Mode">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button class="anim-btn reset-btn" data-word="${index}" data-char="${charIndex}" title="Reset">
                        <i class="fas fa-redo"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    card.innerHTML = `
        <div class="word-header">
            <div class="word-info">
                <div class="word-hanzi">${result.word}</div>
                <div class="word-pinyin">${result.pinyin}</div>
                <div class="word-english">${result.english}</div>
                <span class="word-pos">${result.pos}</span>
            </div>
        </div>
        
        <div class="characters-container">
            ${charactersHtml}
        </div>
        
        <div class="stroke-info">
            <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0;">
                <i class="fas fa-info-circle"></i> Click play to animate, pencil icon for quiz mode
            </p>
        </div>
    `;
    
    // Add event listeners for buttons
    setTimeout(() => {
        card.querySelectorAll('.play-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const wIdx = parseInt(btn.dataset.word);
                const cIdx = parseInt(btn.dataset.char);
                playAnimation(wIdx, cIdx);
            });
        });
        
        card.querySelectorAll('.quiz-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const wIdx = parseInt(btn.dataset.word);
                const cIdx = parseInt(btn.dataset.char);
                startQuiz(wIdx, cIdx);
            });
        });
        
        card.querySelectorAll('.reset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const wIdx = parseInt(btn.dataset.word);
                const cIdx = parseInt(btn.dataset.char);
                resetAnimation(wIdx, cIdx);
            });
        });
    }, 0);
    
    return card;
}

/**
 * Play animation for a character
 */
function playAnimation(wordIndex, charIndex) {
    const instance = writerInstances.find(
        w => w.wordIndex === wordIndex && w.charIndex === charIndex
    );
    
    if (instance && instance.writer) {
        instance.writer.animateCharacter();
    }
}

/**
 * Start quiz mode for a character
 */
function startQuiz(wordIndex, charIndex) {
    const instance = writerInstances.find(
        w => w.wordIndex === wordIndex && w.charIndex === charIndex
    );
    
    if (instance && instance.writer) {
        // Stop any ongoing animation first
        instance.writer.cancelQuiz();
        instance.writer.quiz();
        showToast('Quiz mode: Trace the character!', 'info');
    }
}

/**
 * Reset animation for a character
 */
function resetAnimation(wordIndex, charIndex) {
    const instance = writerInstances.find(
        w => w.wordIndex === wordIndex && w.charIndex === charIndex
    );
    
    if (instance && instance.writer) {
        instance.writer.cancelQuiz();
        // Re-render the character
        const container = document.getElementById(`hanzi-container-${wordIndex}-${charIndex}`);
        if (container) {
            container.innerHTML = '';
        }
        // Re-initialize
        initHanziWriter(instance.character, wordIndex, charIndex);
    }
}

/**
 * Clean up all Hanzi Writer instances
 */
function cleanupWriters() {
    writerInstances.forEach(instance => {
        if (instance.writer) {
            instance.writer.cancelQuiz();
        }
    });
    writerInstances = [];
}

/**
 * Clear search
 */
function clearSearch() {
    searchInput.value = '';
    clearBtn.style.display = 'none';
    searchInput.focus();
    cleanupWriters();
    hideResults();
    hideNoResults();
    showWelcome();
}

// Utility Functions
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

function showResults() {
    resultsSection.classList.remove('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
}

function showWelcome() {
    welcomeMessage.classList.remove('hidden');
}

function hideWelcome() {
    welcomeMessage.classList.add('hidden');
}

function showNoResults() {
    noResults.classList.remove('hidden');
}

function hideNoResults() {
    noResults.classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}