class PDSAApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.games = {
            'eight-queens': {
                name: 'Eight Queens',
                path: '../games/eight_queens/frontend/',
                progress: 0,
                available: false
            },
            'snake-ladder': {
                name: 'Snake & Ladder',
                path: '../games/snake_ladder/frontend/',
                progress: 0,
                available: false
            },
            'traffic-simulation': {
                name: 'Traffic Simulation',
                path: '../games/traffic_simulation/frontend/',
                progress: 0,
                available: false
            },
            'traveling-salesman': {
                name: 'Traveling Salesman',
                path: '../games/traveling_salesman/frontend/',
                progress: 0,
                available: false
            },
            'tower-hanoi': {
                name: 'Tower of Hanoi',
                path: '../games/tower_hanoi/frontend/',
                progress: 0,
                available: false
            }
        };
        
        this.init();
    }

    init() {
        console.log('🎮 PDSA Interactive Games Application Initialized');
        this.checkBackendConnection();
        this.updateProgressBars();
        this.addEventListeners();
    }

    
    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                console.log('✅ Backend connection successful');
                this.updateConnectionStatus('connected');
                await this.checkGameAvailability();
            } else {
                throw new Error('Backend not responding');
            }
        } catch (error) {
            console.log('❌ Backend connection failed:', error.message);
            this.updateConnectionStatus('disconnected');
        }
    }

    updateConnectionStatus(status) {
       
        let indicator = document.getElementById('connection-status');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'connection-status';
            indicator.className = 'fixed top-4 right-4 px-4 py-2 rounded-full text-white text-sm font-medium z-50';
            document.body.appendChild(indicator);
        }

        if (status === 'connected') {
            indicator.className = 'fixed top-4 right-4 px-4 py-2 rounded-full text-white text-sm font-medium z-50 bg-green-500';
            indicator.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Backend Connected';
            indicator.style.display = 'block';
            setTimeout(() => indicator.style.display = 'none', 3000);
        } else {
            indicator.className = 'fixed top-4 right-4 px-4 py-2 rounded-full text-white text-sm font-medium z-50 bg-red-500';
            indicator.innerHTML = '<i class="fas fa-exclamation-circle mr-2"></i>Backend Offline';
        }
    }

    
    async checkGameAvailability() {
        for (let gameId in this.games) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/${gameId}/status`);
                if (response.ok) {
                    this.games[gameId].available = true;
                    this.games[gameId].progress = 100;
                } else {
                    // Check if game files exist
                    const fileResponse = await fetch(`${this.games[gameId].path}index.html`);
                    if (fileResponse.ok) {
                        this.games[gameId].progress = 50;
                    }
                }
            } catch (error) {
                console.log(`Game ${gameId} not available yet`);
            }
        }
        this.updateGameButtons();
        this.updateProgressBars();
    }

    
    updateGameButtons() {
        for (let gameId in this.games) {
            const button = document.querySelector(`button[onclick="loadGame('${gameId}')"]`);
            if (button && this.games[gameId].available) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-play mr-2"></i>Play Now';
                button.classList.remove('opacity-50');
            }
        }
    }

    
    updateProgressBars() {
        document.querySelectorAll('.progress-indicator').forEach((bar, index) => {
            const gameId = Object.keys(this.games)[index];
            if (gameId && this.games[gameId]) {
                const progress = this.games[gameId].progress;
                bar.style.width = `${progress}%`;
                bar.setAttribute('data-progress', progress);
            }
        });
    }

    
    addEventListeners() {
       
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key >= '1' && e.key <= '5') {
                e.preventDefault();
                const gameIndex = parseInt(e.key) - 1;
                const gameId = Object.keys(this.games)[gameIndex];
                if (gameId) this.loadGame(gameId);
            }
        });
    }

    
    loadGame(gameId) {
        if (!this.games[gameId]) {
            console.error(`Game ${gameId} not found`);
            return;
        }

        if (!this.games[gameId].available) {
            this.showNotification(`${this.games[gameId].name} is not available yet`, 'warning');
            return;
        }

        console.log(`🎮 Loading ${this.games[gameId].name}...`);
        
       
        this.showNotification(`Loading ${this.games[gameId].name}...`, 'info');
        
        
        window.location.href = this.games[gameId].path;
    }

    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg text-white font-medium z-50 ${this.getNotificationColor(type)}`;
        notification.innerHTML = `<i class="${this.getNotificationIcon(type)} mr-2"></i>${message}`;
        
        document.body.appendChild(notification);
        
        
        notification.style.opacity = '0';
        notification.style.transform = 'translate(-50%, -20px)';
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translate(-50%, 0)';
            notification.style.transition = 'all 0.3s ease';
        }, 10);
        
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translate(-50%, -20px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationColor(type) {
        const colors = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            warning: 'bg-yellow-500',
            error: 'bg-red-500'
        };
        return colors[type] || colors.info;
    }

    getNotificationIcon(type) {
        const icons = {
            info: 'fas fa-info-circle',
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-triangle',
            error: 'fas fa-exclamation-circle'
        };
        return icons[type] || icons.info;
    }
}


function loadGame(gameId) {
    window.pdsa.loadGame(gameId);
}

function openRepository() {
    window.open('https://github.com/COBSCCOMP251P/PDSA', '_blank');
}

function viewDocs() {
    const docs = [
        'README.md',
        'TEAM_GUIDE.md', 
        'QUICK_REFERENCE.md'
    ];
    
    const docsList = docs.map(doc => 
        `<li><a href="/${doc}" target="_blank" class="text-blue-600 hover:underline">${doc}</a></li>`
    ).join('');
    
    const popup = document.createElement('div');
    popup.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    popup.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-xl font-bold mb-4">📚 Project Documentation</h3>
            <ul class="space-y-2 mb-4">${docsList}</ul>
            <button onclick="this.parentElement.parentElement.remove()" 
                    class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    
    popup.addEventListener('click', (e) => {
        if (e.target === popup) popup.remove();
    });
}


document.addEventListener('DOMContentLoaded', () => {
    window.pdsa = new PDSAApp();
    console.log('🚀 PDSA Application Ready!');
});


if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(registrationError => console.log('SW registration failed'));
    });
}