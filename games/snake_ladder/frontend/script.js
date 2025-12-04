/**
 * Snake and Ladder Game - Frontend JavaScript
 * Handles game interactions, API calls, and UI updates
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Game state
let currentSession = null;
let currentBoardConfig = null;
let currentPlayerName = null;

// DOM Elements
const sections = {
    setup: document.getElementById('setupSection'),
    loading: document.getElementById('loadingSection'),
    game: document.getElementById('gameSection'),
    result: document.getElementById('resultSection'),
    leaderboard: document.getElementById('leaderboardSection'),
    error: document.getElementById('errorSection')
};

const forms = {
    setup: document.getElementById('setupForm'),
    answer: document.getElementById('answerForm')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Setup form
    forms.setup.addEventListener('submit', handleSetupSubmit);
    
    // Answer form
    forms.answer.addEventListener('submit', handleAnswerSubmit);
    
    // Action buttons
    document.getElementById('playAgainBtn')?.addEventListener('click', resetGame);
    document.getElementById('viewLeaderboardBtn')?.addEventListener('click', showLeaderboard);
    document.getElementById('backToGameBtn')?.addEventListener('click', resetGame);
    document.getElementById('retryBtn')?.addEventListener('click', resetGame);
}

/**
 * Handle setup form submission
 */
async function handleSetupSubmit(e) {
    e.preventDefault();
    
    const playerName = document.getElementById('playerName').value.trim();
    const email = document.getElementById('email').value.trim();
    const boardSize = parseInt(document.getElementById('boardSize').value);
    
    // Validation
    if (!playerName) {
        showError('Please enter your name');
        return;
    }
    
    if (boardSize < 6 || boardSize > 12) {
        showError('Board size must be between 6 and 12');
        return;
    }
    
    currentPlayerName = playerName;
    
    // Show loading
    showSection('loading');
    
    try {
        const response = await fetch(`${API_BASE_URL}/snake-ladder/init`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                player_name: playerName,
                email: email || null,
                board_size: boardSize
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to initialize game');
        }
        
        const data = await response.json();
        
        currentSession = data.session_id;
        currentBoardConfig = data.board_config;
        
        // Display game board
        displayGameBoard(data.board_config, data.answer_choices);
        
        showSection('game');
        
    } catch (error) {
        console.error('Setup error:', error);
        showError(error.message || 'Failed to start game. Please try again.');
    }
}

/**
 * Display the game board
 */
function displayGameBoard(boardConfig, answerChoices) {
    // Display board info
    const boardInfo = document.getElementById('boardInfo');
    boardInfo.innerHTML = `
        <strong>Board Size:</strong> ${boardConfig.board_size}×${boardConfig.board_size} 
        (${boardConfig.total_cells} cells)<br>
        <strong>Ladders:</strong> ${boardConfig.num_ladders} | 
        <strong>Snakes:</strong> ${boardConfig.num_snakes}
    `;
    
    // Create board grid
    const boardContainer = document.getElementById('boardContainer');
    boardContainer.innerHTML = '';
    boardContainer.style.gridTemplateColumns = `repeat(${boardConfig.board_size}, 1fr)`;
    
    const totalCells = boardConfig.total_cells;
    const n = boardConfig.board_size;
    
    // Create cells in snake pattern (zigzag)
    for (let row = n - 1; row >= 0; row--) {
        for (let col = 0; col < n; col++) {
            let cellNum;
            if ((n - 1 - row) % 2 === 0) {
                // Left to right
                cellNum = row * n + col + 1;
            } else {
                // Right to left
                cellNum = row * n + (n - 1 - col) + 1;
            }
            
            const cell = createBoardCell(cellNum, boardConfig, totalCells);
            boardContainer.appendChild(cell);
        }
    }
    
    // Display answer choices
    displayAnswerChoices(answerChoices);
}

/**
 * Create a single board cell
 */
function createBoardCell(cellNum, boardConfig, totalCells) {
    const cell = document.createElement('div');
    cell.className = 'board-cell';
    
    let cellContent = '';
    let cellClass = '';
    
    // Check if start or end
    if (cellNum === 1) {
        cellClass = 'cell-start';
        cellContent = '🎯';
    } else if (cellNum === totalCells) {
        cellClass = 'cell-end';
        cellContent = '🏁';
    }
    // Check if ladder start
    else if (boardConfig.ladders[cellNum]) {
        cellClass = 'cell-ladder';
        cellContent = `🪜→${boardConfig.ladders[cellNum]}`;
    }
    // Check if snake head
    else if (boardConfig.snakes[cellNum]) {
        cellClass = 'cell-snake';
        cellContent = `🐍→${boardConfig.snakes[cellNum]}`;
    }
    
    cell.classList.add(cellClass);
    cell.innerHTML = `
        <div class="cell-number">${cellNum}</div>
        ${cellContent ? `<div class="cell-content">${cellContent}</div>` : ''}
    `;
    
    return cell;
}

/**
 * Display answer choices
 */
function displayAnswerChoices(choices) {
    const answerChoices = document.getElementById('answerChoices');
    answerChoices.innerHTML = '';
    
    choices.forEach((choice, index) => {
        const choiceDiv = document.createElement('div');
        choiceDiv.className = 'answer-choice';
        
        const id = `choice${index}`;
        choiceDiv.innerHTML = `
            <input type="radio" id="${id}" name="answer" value="${choice}" required>
            <label for="${id}">${choice} dice throws</label>
        `;
        
        answerChoices.appendChild(choiceDiv);
    });
}

/**
 * Handle answer form submission
 */
async function handleAnswerSubmit(e) {
    e.preventDefault();
    
    const selectedAnswer = document.querySelector('input[name="answer"]:checked');
    
    if (!selectedAnswer) {
        showError('Please select an answer');
        return;
    }
    
    const playerAnswer = parseInt(selectedAnswer.value);
    
    // Show loading
    showSection('loading');
    
    try {
        const response = await fetch(`${API_BASE_URL}/snake-ladder/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSession,
                player_answer: playerAnswer
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit answer');
        }
        
        const data = await response.json();
        
        // Display result
        displayResult(data);
        showSection('result');
        
    } catch (error) {
        console.error('Submit error:', error);
        showError(error.message || 'Failed to submit answer. Please try again.');
    }
}

/**
 * Display game result
 */
function displayResult(data) {
    // Result icon and title
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    
    if (data.is_correct) {
        resultIcon.className = 'result-icon correct';
        resultTitle.textContent = 'Congratulations! 🎉';
        resultTitle.style.color = '#28a745';
    } else {
        resultIcon.className = 'result-icon incorrect';
        resultTitle.textContent = 'Not Quite Right';
        resultTitle.style.color = '#dc3545';
    }
    
    resultMessage.textContent = data.message;
    
    // Result details
    const resultDetails = document.getElementById('resultDetails');
    resultDetails.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Your Answer:</span>
            <span class="detail-value">${data.player_answer} throws</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Correct Answer:</span>
            <span class="detail-value">${data.correct_answer} throws</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Board Size:</span>
            <span class="detail-value">${currentBoardConfig.board_size}×${currentBoardConfig.board_size}</span>
        </div>
    `;
    
    // Algorithm comparison
    const algorithmDetails = document.getElementById('algorithmDetails');
    algorithmDetails.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">BFS Algorithm:</span>
            <span class="detail-value">
                ${data.bfs_result.min_moves} moves in ${data.bfs_result.execution_time_ms.toFixed(3)} ms
            </span>
        </div>
        <div class="detail-row">
            <span class="detail-label">DFS Algorithm:</span>
            <span class="detail-value">
                ${data.dfs_result.min_moves} moves in ${data.dfs_result.execution_time_ms.toFixed(3)} ms
            </span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Speed Comparison:</span>
            <span class="detail-value">
                ${data.bfs_result.execution_time_ms < data.dfs_result.execution_time_ms ? 
                    'BFS was faster' : 'DFS was faster'}
            </span>
        </div>
    `;
    
    // Player statistics
    if (data.player_stats) {
        const playerStats = document.getElementById('playerStats');
        playerStats.innerHTML = `
            <div class="detail-row">
                <span class="detail-label">Total Games:</span>
                <span class="detail-value">${data.player_stats.total_games}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Correct Answers:</span>
                <span class="detail-value">${data.player_stats.correct_answers}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Accuracy:</span>
                <span class="detail-value">${data.player_stats.accuracy}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Avg Execution Time:</span>
                <span class="detail-value">${data.player_stats.avg_execution_time.toFixed(3)} ms</span>
            </div>
        `;
    }
}

/**
 * Show leaderboard
 */
async function showLeaderboard() {
    showSection('loading');
    
    try {
        const response = await fetch(`${API_BASE_URL}/snake-ladder/leaderboard?limit=10`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch leaderboard');
        }
        
        const data = await response.json();
        
        displayLeaderboard(data.leaderboard);
        showSection('leaderboard');
        
    } catch (error) {
        console.error('Leaderboard error:', error);
        showError('Failed to load leaderboard. Please try again.');
    }
}

/**
 * Display leaderboard
 */
function displayLeaderboard(leaderboard) {
    const container = document.getElementById('leaderboardContainer');
    
    if (!leaderboard || leaderboard.length === 0) {
        container.innerHTML = '<p>No players yet. Be the first to play!</p>';
        return;
    }
    
    let html = `
        <table class="leaderboard-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th>Games</th>
                    <th>Correct</th>
                    <th>Accuracy</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    leaderboard.forEach(player => {
        const rankClass = player.rank <= 3 ? `rank-${player.rank}` : 'rank-other';
        html += `
            <tr>
                <td><span class="rank-badge ${rankClass}">${player.rank}</span></td>
                <td>${player.player_name}</td>
                <td>${player.total_games}</td>
                <td>${player.correct_answers}</td>
                <td>${player.accuracy}%</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

/**
 * Reset game to start new round
 */
function resetGame() {
    currentSession = null;
    currentBoardConfig = null;
    
    // Reset forms
    forms.setup.reset();
    forms.answer.reset();
    
    // Show setup section
    showSection('setup');
}

/**
 * Show specific section
 */
function showSection(sectionName) {
    Object.values(sections).forEach(section => {
        section.classList.add('hidden');
    });
    
    if (sections[sectionName]) {
        sections[sectionName].classList.remove('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    showSection('error');
}

/**
 * Utility: Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
