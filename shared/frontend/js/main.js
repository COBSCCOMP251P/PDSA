// Main application JavaScript
class PDSAApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.init();
    }

    init() {
        console.log('PDSA Interactive Games Application Initialized');
        this.checkBackendConnection();
    }

    // Check if backend is running
    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                console.log('✅ Backend connection successful');
                this.updateConnectionStatus('connected');
            } else {
                throw new Error('Backend not responding');
            }
        } catch (error) {
            console.log('❌ Backend connection failed:', error.message);
            this.updateConnectionStatus('disconnected');
        }
    }

    updateConnectionStatus(status) {
        // Add connection indicator to UI if needed
        const indicator = document.createElement('div');
        indicator.className = `fixed top-4 right-4 px-3 py-1 rounded-full text-sm ${
            status === 'connected' 
                ? 'bg-green-500 text-white' 
                : 'bg-red-500 text-white'
        }`;
        indicator.textContent = status === 'connected' ? '🟢 Backend Online' : '🔴 Backend Offline';
        
        // Remove existing indicator
        const existing = document.querySelector('.connection-indicator');
        if (existing) existing.remove();
        
        indicator.classList.add('connection-indicator');
        document.body.appendChild(indicator);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 3000);
    }
}

// Game loading functions (to be implemented by individual games)
function loadGame(gameName) {
    console.log(`Loading game: ${gameName}`);
    
    // This will be updated when games are implemented
    switch(gameName) {
        case 'queens':
            window.location.href = '../../games/eight_queens/frontend/queens.html';
            break;
        case 'snake-ladder':
            window.location.href = '../../games/snake_ladder/frontend/snake-ladder.html';
            break;
        case 'traffic':
            window.location.href = '../../games/traffic_simulation/frontend/traffic.html';
            break;
        case 'tsp':
            window.location.href = '../../games/traveling_salesman/frontend/tsp.html';
            break;
        case 'hanoi':
            window.location.href = '../../games/tower_hanoi/frontend/hanoi.html';
            break;
        default:
            alert('Game not implemented yet!');
    }
}

function loadDashboard() {
    console.log('Loading performance dashboard');
    alert('Performance Dashboard coming soon!');
}

// Utility functions for API calls
class APIClient {
    constructor(baseUrl = 'http://localhost:8000/api') {
        this.baseUrl = baseUrl;
    }

    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('GET request failed:', error);
            throw error;
        }
    }

    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('POST request failed:', error);
            throw error;
        }
    }
}

// Global API client instance
window.apiClient = new APIClient();

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pdsa = new PDSAApp();
});

// Export for use in game modules
window.PDSAApp = PDSAApp;
window.APIClient = APIClient;