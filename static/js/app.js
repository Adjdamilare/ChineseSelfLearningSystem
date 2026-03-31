// Chinese Self Learning System JavaScript

// Audio player functionality
class AudioPlayer {
    constructor() {
        this.currentAudio = null;
        this.currentButton = null;
    }

    async playAudio(ttsUrl, button) {
        // Stop any currently playing audio
        this.stopAllAudio();
        
        // Set current button and add playing state
        this.currentButton = button;
        this.setPlayingState(button, true);
        
        try {
            // Create audio element
            this.currentAudio = new Audio(ttsUrl);
            
            // Handle audio events
            this.currentAudio.onplay = () => {
                this.setPlayingState(button, true);
            };
            
            this.currentAudio.onended = () => {
                this.setPlayingState(button, false);
                this.currentAudio = null;
                this.currentButton = null;
            };
            
            this.currentAudio.onerror = () => {
                console.error('Audio playback error');
                this.setPlayingState(button, false);
                this.currentAudio = null;
                this.currentButton = null;
            };
            
            // Play the audio
            await this.currentAudio.play();
            
        } catch (error) {
            console.error('Error playing audio:', error);
            this.setPlayingState(button, false);
            this.currentAudio = null;
            this.currentButton = null;
        }
    }
    
    stopAllAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }
        
        if (this.currentButton) {
            this.setPlayingState(this.currentButton, false);
        }
        
        this.currentAudio = null;
        this.currentButton = null;
    }
    
    setPlayingState(button, isPlaying) {
        if (isPlaying) {
            button.innerHTML = '⏹️';
            button.disabled = false;
            button.style.background = '#e74c3c';
            button.title = 'Stop audio';
        } else {
            button.innerHTML = '▶️';
            button.disabled = false;
            button.style.background = '#27ae60';
            button.title = 'Play pronunciation';
        }
    }
}

// Initialize audio player globally
const audioPlayer = new AudioPlayer();

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add click listeners to all play buttons
    document.querySelectorAll('.play-btn').forEach(button => {
        button.addEventListener('click', function() {
            const ttsUrl = this.getAttribute('data-tts-url');
            if (ttsUrl) {
                audioPlayer.playAudio(ttsUrl, this);
            }
        });
    });
    
    // Add click listeners to word cards for better UX
    document.querySelectorAll('.word-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons
            if (e.target.closest('.play-btn') || e.target.closest('.add-flashcard-btn')) {
                return;
            }
            const playBtn = this.querySelector('.play-btn');
            if (playBtn) {
                playBtn.click();
            }
        });
    });
});

// Utility functions
function showToast(message, type = 'info') {
    // Create toast element
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
    
    // Add to page
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'fadeIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Make showToast available globally
window.showToast = showToast;
window.audioPlayer = audioPlayer;