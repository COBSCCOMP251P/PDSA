/**
 * Snake and Ladder Game - Frontend JavaScript
 * Handles game interactions, API calls, and UI updates
 */

console.log('=== Script.js loaded ===', new Date().toISOString());

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Game state
let currentSession = null;
let currentBoardConfig = null;
let currentPlayerName = null;
let currentGameResult = null; // Store result for visualization

// Debug: Log when variables change
window.debugGameState = function() {
    console.log('Current Game State:');
    console.log('- currentSession:', currentSession);
    console.log('- currentBoardConfig:', currentBoardConfig);
    console.log('- currentPlayerName:', currentPlayerName);
    console.log('- currentGameResult:', currentGameResult);
};

// DOM Elements
const sections = {
    setup: document.getElementById('setupSection'),
    loading: document.getElementById('loadingSection'),
    game: document.getElementById('gameSection'),
    result: document.getElementById('resultSection'),
    leaderboard: document.getElementById('leaderboardSection'),
    error: document.getElementById('errorSection'),
    pathVisualization: document.getElementById('pathVisualizationSection')
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
    
    // Path visualization buttons
    document.getElementById('showBFSVisualizationBtn')?.addEventListener('click', () => showPathVisualization('bfs'));
    document.getElementById('showDFSVisualizationBtn')?.addEventListener('click', () => showPathVisualization('dfs'));
    document.getElementById('startAnimationBtn')?.addEventListener('click', startPathAnimation);
    document.getElementById('pauseAnimationBtn')?.addEventListener('click', pausePathAnimation);
    document.getElementById('resetAnimationBtn')?.addEventListener('click', resetPathAnimation);
    document.getElementById('closePathBtn')?.addEventListener('click', closePathVisualization);
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
        
        console.log('Game initialized - stored boardConfig:', currentBoardConfig);
        
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
    
    // Only add class if it's not empty
    if (cellClass) {
        cell.classList.add(cellClass);
    }
    
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
        
        // Store result for visualization
        currentGameResult = data;
        
        console.log('Answer submitted - stored gameResult:', currentGameResult);
        console.log('BFS result:', currentGameResult.bfs_result);
        console.log('BFS path:', currentGameResult.bfs_result?.path);
        
        // Display result
        displayResult(data);
        showSection('result');
        
        // Attach visualization button listeners after DOM update
        setTimeout(() => {
            const bfsBtn = document.getElementById('showBFSVisualizationBtn');
            const dfsBtn = document.getElementById('showDFSVisualizationBtn');
            if (bfsBtn) {
                bfsBtn.onclick = () => showPathVisualization('bfs');
                console.log('Attaching click listener to BFS visualization button');
            }
            if (dfsBtn) {
                dfsBtn.onclick = () => showPathVisualization('dfs');
                console.log('Attaching click listener to DFS visualization button');
            }
        }, 100);
        
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
    
    // Algorithm comparison - show both algorithms separately
    const algorithmDetails = document.getElementById('algorithmDetails');
    const bfsFaster = data.bfs_result.execution_time_ms < data.dfs_result.execution_time_ms;
    algorithmDetails.innerHTML = `
        <div style="margin-bottom: 20px; padding: 15px; background: #e3f2fd; border-radius: 8px;">
            <h4 style="color: #1976d2; margin-bottom: 10px;">🔵 BFS (Breadth-First Search)</h4>
            <div class="detail-row">
                <span class="detail-label">Minimum Moves:</span>
                <span class="detail-value">${data.bfs_result.min_moves} throws</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Execution Time:</span>
                <span class="detail-value">${data.bfs_result.execution_time_ms.toFixed(3)} ms ${bfsFaster ? '⚡ (Faster)' : ''}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Path Length:</span>
                <span class="detail-value">${data.bfs_result.path?.length || 0} positions</span>
            </div>
        </div>
        <div style="padding: 15px; background: #fce4ec; border-radius: 8px;">
            <h4 style="color: #c2185b; margin-bottom: 10px;">🔴 DFS (Depth-First Search)</h4>
            <div class="detail-row">
                <span class="detail-label">Minimum Moves:</span>
                <span class="detail-value">${data.dfs_result.min_moves} throws</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Execution Time:</span>
                <span class="detail-value">${data.dfs_result.execution_time_ms.toFixed(3)} ms ${!bfsFaster ? '⚡ (Faster)' : ''}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Path Length:</span>
                <span class="detail-value">${data.dfs_result.path?.length || 0} positions</span>
            </div>
        </div>
        <div class="detail-row" style="margin-top: 15px; font-weight: bold;">
            <span class="detail-label">Winner:</span>
            <span class="detail-value">
                ${bfsFaster ? '🔵 BFS was faster' : '🔴 DFS was faster'} 
                (by ${Math.abs(data.bfs_result.execution_time_ms - data.dfs_result.execution_time_ms).toFixed(3)} ms)
            </span>
        </div>
    `;
    
    // Player statistics
    if (data.player_stats) {
        const playerStats = document.getElementById('playerStats');
        const avgTime = parseFloat(data.player_stats.avg_execution_time) || 0;
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
                <span class="detail-value">${avgTime.toFixed(3)} ms</span>
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
    currentGameResult = null;
    
    console.log('Game reset - all data cleared');
    
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

// ==================== PATH VISUALIZATION ====================

let animationState = {
    path: [],
    currentStep: 0,
    isPlaying: false,
    isPaused: false,
    intervalId: null,
    boardConfig: null,
    algorithm: 'bfs' // Track which algorithm is being visualized
};



/**
 * Show path visualization section
 * @param {string} algorithmType - 'bfs' or 'dfs'
 */
function showPathVisualization(algorithmType = 'bfs') {
    console.log(`=== showPathVisualization called for ${algorithmType.toUpperCase()} ===`);
    console.log('currentBoardConfig:', currentBoardConfig);
    console.log('currentGameResult:', currentGameResult);
    
    // Check if we have game result with path data
    if (!currentBoardConfig) {
        alert('Board config missing! Please start a new game first.');
        console.error('currentBoardConfig is null or undefined');
        return;
    }
    
    if (!currentGameResult) {
        alert('Game result missing! Please submit your answer first.');
        console.error('currentGameResult is null or undefined');
        return;
    }
    
    const algorithmResult = algorithmType === 'bfs' ? currentGameResult.bfs_result : currentGameResult.dfs_result;
    
    if (!algorithmResult) {
        alert(`${algorithmType.toUpperCase()} result missing in game result!`);
        console.error(`currentGameResult.${algorithmType}_result is null or undefined`);
        return;
    }
    
    const pathSection = document.getElementById('pathVisualizationSection');
    const animatedBoardContainer = document.getElementById('animatedBoardContainer');
    const visualizationTitle = document.getElementById('visualizationTitle');
    
    if (!pathSection) {
        alert('Path visualization section not found!');
        return;
    }
    
    // Update title based on algorithm
    const algorithmName = algorithmType === 'bfs' ? 'BFS (Breadth-First Search)' : 'DFS (Depth-First Search)';
    const algorithmEmoji = algorithmType === 'bfs' ? '🔵' : '🔴';
    visualizationTitle.textContent = `${algorithmEmoji} ${algorithmName} Path Visualization`;
    
    // Update info to show algorithm-specific details
    document.getElementById('pathInfo').innerHTML = `
        <p><strong>🎯 Visualizing ${algorithmType.toUpperCase()} Algorithm Solution</strong></p>
        <p><strong>Algorithm:</strong> ${algorithmName}</p>
        <p><strong>Minimum Moves:</strong> ${algorithmResult.min_moves} throws | 
        <strong>Execution Time:</strong> ${algorithmResult.execution_time_ms.toFixed(3)}ms</p>
        <p><strong>Path Length:</strong> ${algorithmResult.path?.length || 0} positions visited</p>
    `;

    // Sync dice styling/label to the selected algorithm so the user can see which path is playing
    const diceEl = document.getElementById('diceValue');
    const diceLabel = document.getElementById('diceLabel');
    diceEl.classList.remove('dice-bfs', 'dice-dfs');
    diceLabel.classList.remove('dice-label-bfs', 'dice-label-dfs');
    const isDFS = algorithmType === 'dfs';
    diceEl.classList.add(isDFS ? 'dice-dfs' : 'dice-bfs');
    diceLabel.classList.add(isDFS ? 'dice-label-dfs' : 'dice-label-bfs');
    diceLabel.textContent = isDFS ? 'Dice Roll — DFS' : 'Dice Roll — BFS';
    
    // Render board for animation (same as displayGameBoard)
    animatedBoardContainer.innerHTML = '';
    animatedBoardContainer.style.gridTemplateColumns = `repeat(${currentBoardConfig.board_size}, 1fr)`;
    
    const totalCells = currentBoardConfig.total_cells;
    const n = currentBoardConfig.board_size;
    
    // Create cells in snake pattern (zigzag)
    for (let row = n - 1; row >= 0; row--) {
        for (let col = 0; col < n; col++) {
            let cellNum;
            if ((n - 1 - row) % 2 === 0) {
                cellNum = row * n + col + 1;
            } else {
                cellNum = row * n + (n - 1 - col) + 1;
            }
            
            const cell = createBoardCell(cellNum, currentBoardConfig, totalCells);
            animatedBoardContainer.appendChild(cell);
        }
    }
    
    // Show the section
    pathSection.classList.remove('hidden');
    pathSection.scrollIntoView({ behavior: 'smooth' });
    
    // Reset animation state and store the selected algorithm's path
    animationState.path = algorithmResult.path || [];
    animationState.algorithm = algorithmType;
    resetPathAnimation();
}

/**
 * Start path animation
 */
function startPathAnimation() {
    if (!currentBoardConfig) {
        alert('No game data available');
        return;
    }
    
    animationState.isPlaying = true;
    animationState.isPaused = false;
    
    document.getElementById('startAnimationBtn').disabled = true;
    document.getElementById('pauseAnimationBtn').disabled = false;
    
    // Simulate BFS path (1 to target with random dice rolls)
    animatePath();
}

/**
 * Pause animation
 */
function pausePathAnimation() {
    animationState.isPaused = true;
    animationState.isPlaying = false;
    
    if (animationState.intervalId) {
        clearTimeout(animationState.intervalId);
    }
    
    document.getElementById('startAnimationBtn').disabled = false;
    document.getElementById('pauseAnimationBtn').disabled = true;
    
    document.getElementById('moveStatus').textContent = 'Paused';
}

/**
 * Reset animation
 */
function resetPathAnimation() {
    animationState.currentStep = 0;
    animationState.isPlaying = false;
    animationState.isPaused = false;
    
    if (animationState.intervalId) {
        clearTimeout(animationState.intervalId);
    }
    
    document.getElementById('startAnimationBtn').disabled = false;
    document.getElementById('pauseAnimationBtn').disabled = true;
    
    document.getElementById('diceValue').textContent = '?';
    const diceLabel = document.getElementById('diceLabel');
    const diceValue = document.getElementById('diceValue');
    diceValue.classList.remove('dice-bfs', 'dice-dfs');
    diceLabel.classList.remove('dice-label-bfs', 'dice-label-dfs');
    const isDFS = animationState.algorithm === 'dfs';
    diceValue.classList.add(isDFS ? 'dice-dfs' : 'dice-bfs');
    diceLabel.classList.add(isDFS ? 'dice-label-dfs' : 'dice-label-bfs');
    diceLabel.textContent = isDFS ? 'Dice Roll — DFS' : 'Dice Roll — BFS';
    document.getElementById('currentPos').textContent = '1';
    document.getElementById('nextPos').textContent = '-';
    document.getElementById('throwsCount').textContent = '0';
    document.getElementById('moveStatus').textContent = 'Ready';
    document.getElementById('moveStatus').className = 'info-value';
    
    // Clear all position highlights
    const cells = document.querySelectorAll('#animatedBoardContainer .cell');
    cells.forEach(cell => {
        cell.classList.remove('player-position', 'visited', 'next-move');
    });
}

/**
 * Close path visualization
 */
function closePathVisualization() {
    document.getElementById('pathVisualizationSection').classList.add('hidden');
    resetPathAnimation();
}

/**
 * Animate the path from start to end using BFS path
 */
function animatePath() {
    const path = animationState.path;
    
    // If no path available, use simulation
    if (!path || path.length === 0) {
        animatePathSimulation();
        return;
    }
    
    let stepIndex = 0;
    let throwCount = 0;
    
    // Highlight starting position
    highlightCell(path[0], 'player-position');
    document.getElementById('currentPos').textContent = path[0];
    document.getElementById('moveStatus').textContent = 'Starting...';
    
    function makeMove() {
        if (!animationState.isPlaying || stepIndex >= path.length - 1) {
            if (stepIndex >= path.length - 1) {
                document.getElementById('moveStatus').textContent = 'Completed! 🎉';
                document.getElementById('moveStatus').className = 'info-value status-complete';
                document.getElementById('startAnimationBtn').disabled = false;
                document.getElementById('pauseAnimationBtn').disabled = true;
            }
            return;
        }
        
        const currentPosition = path[stepIndex];
        const nextPosition = path[stepIndex + 1];
        
        throwCount++;
        document.getElementById('throwsCount').textContent = throwCount;
        
        // Calculate the actual dice roll by reverse-engineering from the path
        // The next position might be result of: currentPos + dice, or a ladder/snake
        let diceRoll = 1;
        let landedPosition = currentPosition + 1;
        
        // Try to figure out what dice roll was used
        // Check all possible dice rolls (1-6) and see which one leads to nextPosition
        for (let roll = 1; roll <= 6; roll++) {
            let testPosition = currentPosition + roll;
            
            // Check if this leads to a ladder
            if (currentBoardConfig.ladders[testPosition]) {
                if (currentBoardConfig.ladders[testPosition] === nextPosition) {
                    diceRoll = roll;
                    landedPosition = testPosition;
                    break;
                }
            }
            // Check if this leads to a snake
            else if (currentBoardConfig.snakes[testPosition]) {
                if (currentBoardConfig.snakes[testPosition] === nextPosition) {
                    diceRoll = roll;
                    landedPosition = testPosition;
                    break;
                }
            }
            // Check if it's a direct move
            else if (testPosition === nextPosition) {
                diceRoll = roll;
                landedPosition = testPosition;
                break;
            }
        }
        
        // Animate dice
        const diceElement = document.getElementById('diceValue');
        diceElement.classList.add('rolling');
        diceElement.textContent = '🎲';
        
        setTimeout(() => {
            diceElement.textContent = diceRoll;
            diceElement.classList.remove('rolling');
            
            // Determine what happened in this move
            // Check for ladder
            if (currentBoardConfig.ladders[landedPosition]) {
                const ladderEnd = currentBoardConfig.ladders[landedPosition];
                document.getElementById('moveStatus').textContent = `Rolled ${diceRoll} → Ladder! ${landedPosition} → ${ladderEnd} 🪜`;
                document.getElementById('moveStatus').className = 'info-value status-ladder';
            }
            // Check for snake
            else if (currentBoardConfig.snakes[landedPosition]) {
                const snakeEnd = currentBoardConfig.snakes[landedPosition];
                document.getElementById('moveStatus').textContent = `Rolled ${diceRoll} → Snake! ${landedPosition} → ${snakeEnd} 🐍`;
                document.getElementById('moveStatus').className = 'info-value status-snake';
            } else {
                document.getElementById('moveStatus').textContent = `Rolled ${diceRoll} → Moving to ${nextPosition}`;
                document.getElementById('moveStatus').className = 'info-value status-moving';
            }
            
            // Update UI
            document.getElementById('nextPos').textContent = nextPosition;
            
            // Remove previous highlight
            clearHighlight(currentPosition);
            
            // Mark as visited
            if (currentPosition !== path[0]) {
                highlightCell(currentPosition, 'visited');
            }
            
            // Highlight next position
            highlightCell(nextPosition, 'player-position');
            document.getElementById('currentPos').textContent = nextPosition;
            
            // Move to next step
            stepIndex++;
            
            // Continue animation
            if (stepIndex < path.length - 1 && animationState.isPlaying) {
                animationState.intervalId = setTimeout(makeMove, 1500);
            } else if (stepIndex >= path.length - 1) {
                document.getElementById('moveStatus').textContent = 'Completed! 🎉';
                document.getElementById('moveStatus').className = 'info-value status-complete';
                document.getElementById('startAnimationBtn').disabled = false;
                document.getElementById('pauseAnimationBtn').disabled = true;
            }
        }, 600);
    }
    
    // Start first move
    animationState.intervalId = setTimeout(makeMove, 500);
}

/**
 * Highlight a cell on the animated board
 */
function highlightCell(cellNum, className) {
    const cells = document.querySelectorAll('#animatedBoardContainer .cell');
    cells.forEach(cell => {
        const cellNumber = parseInt(cell.querySelector('.cell-number')?.textContent);
        if (cellNumber === cellNum) {
            cell.classList.add(className);
        }
    });
}

/**
 * Clear highlight from a cell
 */
function clearHighlight(cellNum) {
    const cells = document.querySelectorAll('#animatedBoardContainer .cell');
    cells.forEach(cell => {
        const cellNumber = parseInt(cell.querySelector('.cell-number')?.textContent);
        if (cellNumber === cellNum) {
            cell.classList.remove('player-position', 'next-move');
        }
    });
}

/**
 * Utility: Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
