// Eight Queens Game - JavaScript
// Global game state
let gameState = {
    playerId: null,
    playerName: '',
    playerEmail: '',
    isAuthenticated: false,
    selectedDifficulty: '',
    selectedAlgorithm: 'sequential', // Default to sequential
    sessionId: null,
    board: new Array(8).fill(-1),
    gameSettings: {},
    startTime: null,
    timer: null,
    moveHistory: [],
    hintsUsed: 0,
    undosUsed: 0,
    score: 0,
    isDarkMode: false
};

// API Configuration
const API_BASE = '/api/eight-queens-game';

// Initialize game on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Eight Queens Game loaded');
    setupDifficultyCards();
    
    // Check if returning from stats page
    if (localStorage.getItem('returnToDifficulty') === 'true') {
        localStorage.removeItem('returnToDifficulty');
        // Restore player info from localStorage
        const savedPlayerName = localStorage.getItem('playerName');
        const savedPlayerId = localStorage.getItem('playerId');
        if (savedPlayerName) {
            gameState.playerName = savedPlayerName;
            gameState.playerId = savedPlayerId;
        }
        showDifficultyScreen();
    }
});

// Show difficulty screen directly
function showDifficultyScreen() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('newPlayerScreen')?.classList.add('hidden');
    document.getElementById('existingPlayerScreen')?.classList.add('hidden');
    document.getElementById('difficultyScreen').classList.remove('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
}

// =============================================
// THEME TOGGLE
// =============================================

function toggleGameTheme() {
    const gameScreen = document.getElementById('gameScreen');
    const themeIcon = document.querySelector('.theme-icon');
    
    gameState.isDarkMode = !gameState.isDarkMode;
    
    if (gameState.isDarkMode) {
        gameScreen.classList.remove('game-screen-light');
        gameScreen.classList.add('game-screen-dark');
        themeIcon.textContent = '☀️';
    } else {
        gameScreen.classList.remove('game-screen-dark');
        gameScreen.classList.add('game-screen-light');
        themeIcon.textContent = '🌙';
    }
}

// =============================================
// NAVIGATION FUNCTIONS
// =============================================

function showNewPlayerForm() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('newPlayerScreen').classList.remove('hidden');
    document.getElementById('existingPlayerScreen').classList.add('hidden');
    document.getElementById('difficultyScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('successScreen').classList.add('hidden');
    document.getElementById('duplicateScreen').classList.add('hidden');
    
    document.getElementById('newPlayerUsername').focus();
}

function showExistingPlayerForm() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('newPlayerScreen').classList.add('hidden');
    document.getElementById('existingPlayerScreen').classList.remove('hidden');
    document.getElementById('difficultyScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('successScreen').classList.add('hidden');
    document.getElementById('duplicateScreen').classList.add('hidden');
    
    document.getElementById('existingPlayerUsername').focus();
}

function goBackToWelcome() {
    document.getElementById('welcomeScreen').classList.remove('hidden');
    document.getElementById('newPlayerScreen').classList.add('hidden');
    document.getElementById('existingPlayerScreen').classList.add('hidden');
    document.getElementById('difficultyScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('successScreen').classList.add('hidden');
    document.getElementById('duplicateScreen').classList.add('hidden');
    
    // Clear error messages
    const errorDiv = document.getElementById('playerNotFoundHelp');
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}

function showDifficultySelection() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('newPlayerScreen').classList.add('hidden');
    document.getElementById('existingPlayerScreen').classList.add('hidden');
    document.getElementById('difficultyScreen').classList.remove('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('successScreen').classList.add('hidden');
    document.getElementById('duplicateScreen').classList.add('hidden');
}

// =============================================
// AUTHENTICATION FUNCTIONS
// =============================================

async function createNewPlayer() {
    const username = document.getElementById('newPlayerUsername').value.trim();
    const errorBox = document.getElementById('usernameError');
    
    // Hide previous error
    errorBox.classList.add('hidden');
    
    if (!username) {
        showUsernameError('Please enter a username');
        return;
    }
    
    if (username.length < 3) {
        showUsernameError('Username must be at least 3 characters');
        return;
    }
    
    if (username.length > 20) {
        showUsernameError('Username must be 20 characters or less');
        return;
    }
    
    // Check for valid characters (letters, numbers, underscore)
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showUsernameError('Username can only contain letters, numbers, and underscores');
        return;
    }
    
    try {
        const btn = document.getElementById('createPlayerBtn');
        btn.disabled = true;
        btn.textContent = 'Creating...';
        
        const response = await fetch(`${API_BASE}/players/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: username })
        });
        
        const result = await response.json();
        
        if (response.status === 409) {
            showUsernameError('Username already taken. Please choose another.');
            return;
        }
        
        if (result.status === 'success') {
            gameState.playerId = result.data.player_id;
            gameState.playerName = username;
            gameState.isAuthenticated = true;
            
            // Save to localStorage for stats page
            localStorage.setItem('playerName', username);
            localStorage.setItem('playerId', result.data.player_id);
            
            showDifficultySelection();
        } else {
            showUsernameError(result.detail || 'Failed to create account. Please try again.');
        }
        
    } catch (error) {
        console.error('Create player error:', error);
        showUsernameError('Connection error. Please try again.');
    } finally {
        const btn = document.getElementById('createPlayerBtn');
        btn.disabled = false;
        btn.textContent = 'Create Account';
    }
}

function showUsernameError(message) {
    const errorBox = document.getElementById('usernameError');
    errorBox.textContent = message;
    errorBox.classList.remove('hidden');
}

async function loginExistingPlayer() {
    const username = document.getElementById('existingPlayerUsername').value.trim();
    
    if (!username) {
        alert('Please enter your username!');
        return;
    }
    
    try {
        const btn = document.getElementById('loginPlayerBtn');
        btn.disabled = true;
        btn.textContent = 'Logging in...';
        
        const response = await fetch(`${API_BASE}/players/${encodeURIComponent(username)}/profile`);
        
        if (response.status === 404) {
            document.getElementById('playerNotFoundHelp').classList.remove('hidden');
            alert('Username not found. Please check your spelling or create a new account.');
            return;
        }
        
        const result = await response.json();
        
        if (result.status === 'success' && result.data.player_info) {
            const playerInfo = result.data.player_info;
            gameState.playerId = playerInfo.id;
            gameState.playerName = playerInfo.name;
            gameState.playerEmail = playerInfo.email || '';
            gameState.isAuthenticated = true;
            
            // Save to localStorage for stats page
            localStorage.setItem('playerName', playerInfo.name);
            localStorage.setItem('playerId', playerInfo.id);
            
            alert(`Welcome back, ${playerInfo.name}!`);
            showDifficultySelection();
        } else {
            alert('Failed to login. Please try again.');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        alert('Error logging in. Please try again.');
    } finally {
        const btn = document.getElementById('loginPlayerBtn');
        btn.disabled = false;
        btn.textContent = 'Login';
    }
}

// =============================================
// DIFFICULTY SELECTION
// =============================================

function setupDifficultyCards() {
    const cards = document.querySelectorAll('.diff-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const difficulty = card.dataset.difficulty;
            selectDifficulty(difficulty);
        });
    });
}

function selectDifficulty(difficulty) {
    document.querySelectorAll('.diff-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    const selectedCard = document.querySelector(`[data-difficulty="${difficulty}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    gameState.selectedDifficulty = difficulty;
    document.getElementById('startGameBtn').disabled = false;
}

async function startSelectedGame() {
    if (!gameState.selectedDifficulty) {
        alert('Please select a difficulty level!');
        return;
    }
    
    if (!gameState.playerName) {
        alert('Please login or create an account first!');
        return;
    }
    
    // Get selected algorithm from radio buttons
    const algorithmRadio = document.querySelector('input[name="algorithm"]:checked');
    gameState.selectedAlgorithm = algorithmRadio ? algorithmRadio.value : 'sequential';
    
    try {
        const response = await fetch(`${API_BASE}/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_name: gameState.playerName,
                difficulty: gameState.selectedDifficulty,
                algorithm_type: gameState.selectedAlgorithm
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            gameState.sessionId = result.data.session_id;
            gameState.gameSettings = result.data.settings;
            gameState.board = result.game_state.board;
            gameState.startTime = Date.now();
            
            initializeGameScreen();
        } else {
            alert(result.message || 'Failed to start game');
        }
        
    } catch (error) {
        console.error('Start game error:', error);
        alert('Failed to start game. Please try again.');
    }
}

// =============================================
// GAME SCREEN
// =============================================

function initializeGameScreen() {
    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('newPlayerScreen').classList.add('hidden');
    document.getElementById('existingPlayerScreen').classList.add('hidden');
    document.getElementById('difficultyScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.remove('hidden');
    document.getElementById('successScreen').classList.add('hidden');
    document.getElementById('duplicateScreen').classList.add('hidden');
    
    setupGameDisplay();
    createChessBoard();
    startGameTimer();
    updateGameStats();
}

function setupGameDisplay() {
    document.getElementById('playerDisplay').textContent = gameState.playerName;
    document.getElementById('difficultyDisplay').textContent = 
        gameState.selectedDifficulty.charAt(0).toUpperCase() + gameState.selectedDifficulty.slice(1);
    document.getElementById('algorithmDisplay').textContent = 
        gameState.selectedAlgorithm === 'threaded' ? 'Multi-Threaded' : 'Sequential';
    
    const hintCounter = document.getElementById('hintCounter');
    const undoCounter = document.getElementById('undoCounter');
    const undoBtn = document.getElementById('undoBtn');
    
    // Set hint counter
    if (gameState.gameSettings.max_hints === 999) {
        hintCounter.textContent = '(∞)';
    } else {
        hintCounter.textContent = `(${gameState.gameSettings.max_hints})`;
    }
    
    // Set undo counter based on difficulty
    if (gameState.gameSettings.undo_allowed === true) {
        undoBtn.style.display = 'flex';
        if (gameState.selectedDifficulty === 'medium') {
            undoCounter.textContent = '(5)';
        } else {
            undoCounter.textContent = '(∞)';
        }
    } else {
        // Hard mode - no undo allowed
        undoBtn.style.display = 'none';
    }
    
    const timeLimitElement = document.getElementById('timeLimit');
    if (timeLimitElement) {
        if (gameState.gameSettings.time_limit_seconds) {
            const minutes = Math.floor(gameState.gameSettings.time_limit_seconds / 60);
            timeLimitElement.textContent = `Limit: ${minutes} min`;
        } else {
            timeLimitElement.textContent = 'No limit';
        }
    }
}

function createChessBoard() {
    const board = document.getElementById('chessBoard');
    board.innerHTML = '';
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const cell = document.createElement('div');
            // Determine cell color (checkerboard pattern)
            const isLight = (row + col) % 2 === 0;
            cell.className = `cell ${isLight ? 'light' : 'dark'}`;
            cell.dataset.row = row;
            cell.dataset.col = col;
            
            // Check if queen should be placed
            if (gameState.board[row] === col) {
                cell.innerHTML = '<span class="queen">♛</span>';
                
                // Mark pre-placed queens in Easy mode (locked, can't remove)
                if (gameState.selectedDifficulty === 'easy') {
                    if ((row === 0 && col === 0) || (row === 1 && col === 2)) {
                        cell.classList.add('pre-placed');
                        cell.title = 'Pre-placed queen (locked)';
                    }
                }
            }
            
            cell.addEventListener('click', () => makeMove(row, col));
            board.appendChild(cell);
        }
    }
    
    if (gameState.gameSettings.visual_hints) {
        highlightConflicts();
    }
}

async function makeMove(row, col) {
    try {
        const action = gameState.board[row] === col ? 'remove' : 'place';
        
        // Prevent removing pre-placed queens in Easy mode
        if (gameState.selectedDifficulty === 'easy' && action === 'remove') {
            // Check if this is a pre-placed queen (row 0 or 1 in original positions)
            if ((row === 0 && col === 0) || (row === 1 && col === 2)) {
                document.getElementById('moveStatus').textContent = '⚠️ Cannot remove pre-placed queens!';
                document.getElementById('moveStatus').style.color = '#f59e0b';
                return;
            }
        }
        
        const response = await fetch(`${API_BASE}/game/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                row: row,
                col: col,
                action: action
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            gameState.board = result.game_state.board;
            gameState.moveHistory.push({ row, col, action });
            
            createChessBoard();
            updateGameStats();
            updateMoveStatus(action, row, col, result.game_state.conflicts);
            
            if (result.game_state.is_complete && result.game_state.is_valid) {
                await submitSolution();
            }
        } else {
            alert(result.message || 'Move failed');
        }
        
    } catch (error) {
        console.error('Make move error:', error);
        alert('Failed to make move');
    }
}

function highlightConflicts() {
    const conflicts = findConflicts(gameState.board);
    
    conflicts.forEach(({row, col}) => {
        const square = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        if (square) {
            square.classList.add('conflict');
        }
    });
}

function findConflicts(board) {
    const conflicts = [];
    
    for (let row = 0; row < 8; row++) {
        if (board[row] === -1) continue;
        
        const col = board[row];
        
        for (let otherRow = 0; otherRow < 8; otherRow++) {
            if (otherRow === row || board[otherRow] === -1) continue;
            
            const otherCol = board[otherRow];
            
            if (col === otherCol || Math.abs(row - otherRow) === Math.abs(col - otherCol)) {
                conflicts.push({ row, col });
                break;
            }
        }
    }
    
    return conflicts;
}

// =============================================
// GAME ACTIONS
// =============================================

async function getHint() {
    try {
        const hintsRemaining = gameState.gameSettings.max_hints - gameState.hintsUsed;
        if (gameState.gameSettings.max_hints !== 999 && hintsRemaining <= 0) {
            alert('No more hints available!');
            return;
        }
        
        const response = await fetch(`${API_BASE}/game/hint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                hint_type: 'safe_position',
                current_board: gameState.board
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            gameState.hintsUsed++;
            displayHint(result.data.hint);
            updateHintButton();
            updateGameStats();
        }
        
    } catch (error) {
        console.error('Hint error:', error);
        alert('Failed to get hint');
    }
}

function displayHint(hint) {
    document.querySelectorAll('.hint').forEach(sq => sq.classList.remove('hint'));
    
    if (hint.type === 'safe_positions' && hint.positions) {
        hint.positions.forEach(([row, col]) => {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (cell) cell.classList.add('hint');
        });
        
        alert(hint.message);
        
        setTimeout(() => {
            document.querySelectorAll('.hint').forEach(sq => sq.classList.remove('hint'));
        }, 5000);
    }
}

function undoMove() {
    // Hard mode - no undo allowed
    if (gameState.selectedDifficulty === 'hard') {
        alert('Undo is not available in Hard mode!');
        return;
    }
    
    if (gameState.moveHistory.length === 0) {
        alert('No moves to undo');
        return;
    }
    
    if (gameState.selectedDifficulty === 'medium' && gameState.undosUsed >= 5) {
        alert('No more undos available!');
        return;
    }
    
    const lastMove = gameState.moveHistory.pop();
    
    // Prevent undoing pre-placed queens in Easy mode
    if (gameState.selectedDifficulty === 'easy' && lastMove.row < 2 && lastMove.action === 'remove') {
        // This was an undo of a pre-placed queen removal, don't allow
        gameState.moveHistory.push(lastMove); // Put it back
        alert('Cannot undo pre-placed queens!');
        return;
    }
    
    if (lastMove.action === 'place') {
        gameState.board[lastMove.row] = -1;
    } else {
        gameState.board[lastMove.row] = lastMove.col;
    }
    
    gameState.undosUsed++;
    
    createChessBoard();
    updateGameStats();
    updateUndoButton();
}

async function resetGame() {
    if (confirm('Reset the game? All progress will be lost.')) {
        try {
            // Call server reset endpoint
            const response = await fetch(`${API_BASE}/game/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: gameState.sessionId
                })
            });
            
            if (!response.ok) {
                console.error('Reset response not ok:', response.status);
                // Still try to reset locally
                resetLocalGame();
                return;
            }
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Update local state with reset board
                gameState.board = result.game_state.board;
                gameState.hintsUsed = 0;
                gameState.undosUsed = 0;
                gameState.moveHistory = [];
                
                // Reset timer
                if (gameState.timerInterval) {
                    clearInterval(gameState.timerInterval);
                }
                gameState.startTime = Date.now();
                startGameTimer();
                
                // Reset display
                setupGameDisplay();
                createChessBoard();
                updateGameStats();
                
                // Reset status message
                document.getElementById('statusMessage').textContent = 'Game reset! Place your queens on the board.';
            } else {
                // Server returned error, reset locally
                resetLocalGame();
            }
        } catch (error) {
            console.error('Reset error:', error);
            // Fall back to local reset
            resetLocalGame();
        }
    }
}

function resetLocalGame() {
    // Create initial board based on difficulty (same as server logic)
    let initialBoard = [-1, -1, -1, -1, -1, -1, -1, -1];
    if (gameState.selectedDifficulty === 'easy') {
        initialBoard[0] = 0;
        initialBoard[1] = 2;
    }
    
    gameState.board = initialBoard;
    gameState.hintsUsed = 0;
    gameState.undosUsed = 0;
    gameState.moveHistory = [];
    
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
    }
    gameState.startTime = Date.now();
    startGameTimer();
    
    setupGameDisplay();
    createChessBoard();
    updateGameStats();
    
    document.getElementById('statusMessage').textContent = 'Game reset! Place your queens on the board.';
}

function exitGame() {
    if (confirm('Exit game? Your progress will be saved as incomplete.')) {
        showDifficultySelection();
    }
}

// =============================================
// GAME COMPLETION
// =============================================

async function submitSolution() {
    try {
        const completionTime = Math.floor((Date.now() - gameState.startTime) / 1000);
        
        const response = await fetch(`${API_BASE}/game/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                solution: gameState.board,
                completion_time_seconds: completionTime,
                hints_used: gameState.hintsUsed,
                undo_count: gameState.undosUsed
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            gameState.score = result.data.score;
            showSuccessScreen(result.data);
        } else if (result.status === 'duplicate') {
            showDuplicateScreen(result);
        } else {
            alert(result.message || 'Failed to submit solution');
        }
        
    } catch (error) {
        console.error('Submit error:', error);
        alert('Failed to submit solution');
    }
}

function showSuccessScreen(submissionData) {
    if (gameState.timer) clearInterval(gameState.timer);
    
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('successScreen').classList.remove('hidden');
    
    // Check if all 92 solutions were just completed
    if (submissionData.all_found) {
        document.getElementById('successTitle').innerHTML = '🏆 ALL 92 SOLUTIONS FOUND!';
        document.getElementById('successMessage').innerHTML = 
            `<strong>INCREDIBLE!</strong> You found the 92nd and final solution!<br>` +
            `The challenge has been reset for new players.`;
        
        // Show special progress
        document.getElementById('solutionProgress').classList.remove('hidden');
        document.getElementById('foundCount').textContent = '92';
        document.getElementById('totalCount').textContent = '92';
        document.getElementById('progressFill').style.width = '100%';
        document.getElementById('discoveryStatus').textContent = 'Final Solution!';
        document.getElementById('discoveryStatus').className = 'fs-value status-new';
    }
    // Regular new discovery
    else if (submissionData.is_new_discovery) {
        document.getElementById('successTitle').textContent = 'New Solution Discovered!';
        document.getElementById('successMessage').textContent = 
            `You found a unique solution! This is solution #${submissionData.solutions_found} of 92!`;
        
        // Show progress
        document.getElementById('solutionProgress').classList.remove('hidden');
        document.getElementById('foundCount').textContent = submissionData.solutions_found;
        document.getElementById('totalCount').textContent = submissionData.total_solutions;
        const progressPercent = (submissionData.solutions_found / submissionData.total_solutions) * 100;
        document.getElementById('progressFill').style.width = progressPercent + '%';
        document.getElementById('discoveryStatus').textContent = 'New!';
        document.getElementById('discoveryStatus').className = 'fs-value status-new';
    } else {
        document.getElementById('successTitle').textContent = 'Congratulations!';
        document.getElementById('successMessage').textContent = 
            'You successfully solved the Eight Queens puzzle!';
        document.getElementById('discoveryStatus').textContent = 'Valid';
        document.getElementById('discoveryStatus').className = 'fs-value status-found';
    }
    
    document.getElementById('finalScore').textContent = submissionData.score;
    document.getElementById('finalTime').textContent = formatTime(submissionData.completion_time);
    document.getElementById('finalHints').textContent = submissionData.hints_used;
    
    // Display Algorithm Comparison (PDSA Requirement)
    if (submissionData.algorithm_comparison) {
        const compSection = document.getElementById('algorithmComparison');
        compSection.classList.remove('hidden');
        
        document.getElementById('seqTimeDisplay').textContent = 
            submissionData.algorithm_comparison.sequential_time_ms.toFixed(3) + ' ms';
        document.getElementById('threadTimeDisplay').textContent = 
            submissionData.algorithm_comparison.threaded_time_ms.toFixed(3) + ' ms';
        document.getElementById('speedupDisplay').textContent = 
            submissionData.algorithm_comparison.speedup;
    }
}

function showDuplicateScreen(result) {
    if (gameState.timer) clearInterval(gameState.timer);
    
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('duplicateScreen').classList.remove('hidden');
    
    // Update who found it before
    if (result.data && result.data.found_by) {
        document.getElementById('previousFinder').textContent = result.data.found_by;
    }
}

function playAgain() {
    gameState.selectedDifficulty = '';
    gameState.board = new Array(8).fill(-1);
    gameState.hintsUsed = 0;
    gameState.undosUsed = 0;
    gameState.moveHistory = [];
    
    showDifficultySelection();
    
    document.querySelectorAll('.diff-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.getElementById('startGameBtn').disabled = true;
}

// =============================================
// LEADERBOARD
// =============================================

async function viewLeaderboard() {
    document.getElementById('leaderboardModal').classList.remove('hidden');
    await showLeaderboard(gameState.selectedDifficulty || 'easy');
}

async function showLeaderboard(difficulty) {
    try {
        const response = await fetch(`${API_BASE}/leaderboards/${difficulty}?limit=20`);
        const result = await response.json();
        
        if (result.status === 'success') {
            displayLeaderboardData(result.data.leaderboard);
        }
        
    } catch (error) {
        console.error('Leaderboard error:', error);
        document.getElementById('leaderboardContent').innerHTML = 
            '<p style="text-align:center;color:#999;">Failed to load leaderboard</p>';
    }
}

function displayLeaderboardData(leaderboard) {
    const content = document.getElementById('leaderboardContent');
    
    if (!leaderboard || leaderboard.length === 0) {
        content.innerHTML = '<p style="text-align:center;color:#999;">No scores yet. Be the first!</p>';
        return;
    }
    
    const table = `
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:#f8f9fa;">
                    <th style="padding:10px;text-align:left;">Rank</th>
                    <th style="padding:10px;text-align:left;">Player</th>
                    <th style="padding:10px;text-align:center;">Score</th>
                    <th style="padding:10px;text-align:center;">Time</th>
                    <th style="padding:10px;text-align:center;">Hints</th>
                </tr>
            </thead>
            <tbody>
                ${leaderboard.map((entry, index) => `
                    <tr style="border-bottom:1px solid #eee;">
                        <td style="padding:10px;">${index + 1}</td>
                        <td style="padding:10px;">${entry.player_name}</td>
                        <td style="padding:10px;text-align:center;font-weight:bold;">${entry.score}</td>
                        <td style="padding:10px;text-align:center;">${formatTime(entry.completion_time)}</td>
                        <td style="padding:10px;text-align:center;">${entry.hints_used}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    content.innerHTML = table;
}

function closeLeaderboard() {
    document.getElementById('leaderboardModal').classList.add('hidden');
}

// =============================================
// TIMER & STATS
// =============================================

function startGameTimer() {
    gameState.startTime = Date.now();
    
    gameState.timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - gameState.startTime) / 1000);
        document.getElementById('gameTimer').textContent = formatTime(elapsed);
        
        if (gameState.gameSettings.time_limit_seconds && elapsed >= gameState.gameSettings.time_limit_seconds) {
            clearInterval(gameState.timer);
            handleTimeUp();
        }
    }, 1000);
}

function handleTimeUp() {
    // Disable all game interactions
    document.querySelectorAll('.cell').forEach(cell => {
        cell.style.pointerEvents = 'none';
        cell.style.opacity = '0.7';
    });
    document.getElementById('hintBtn').disabled = true;
    document.getElementById('undoBtn').disabled = true;
    document.getElementById('submitBtn').disabled = true;
    
    // Show time up message
    const statusMsg = document.getElementById('statusMessage');
    if (statusMsg) {
        statusMsg.textContent = "⏰ Time's up! Game over.";
        statusMsg.style.color = '#ef4444';
    }
    
    // Show alert with options
    setTimeout(() => {
        if (confirm("Time's up! Your game has ended.\n\nWould you like to try again?")) {
            playAgain();
        } else {
            exitGame();
        }
    }, 500);
}

function updateGameStats() {
    const queensPlaced = gameState.board.filter(pos => pos !== -1).length;
    const conflicts = findConflicts(gameState.board).length;
    
    document.getElementById('queensCount').textContent = `${queensPlaced}/8`;
    document.getElementById('conflictCount').textContent = conflicts;
    document.getElementById('moveCount').textContent = gameState.moveHistory.length;
    document.getElementById('hintsUsed').textContent = gameState.hintsUsed;
    document.getElementById('undosUsed').textContent = gameState.undosUsed;
    
    const baseScore = gameState.gameSettings.base_score || 50;
    const timeBonus = Math.max(0, 300 - Math.floor((Date.now() - gameState.startTime) / 1000));
    const hintPenalty = gameState.hintsUsed * 10;
    const estimatedScore = Math.max(0, baseScore + timeBonus - hintPenalty);
    document.getElementById('currentScore').textContent = estimatedScore;
}

function updateHintButton() {
    const hintsRemaining = gameState.gameSettings.max_hints - gameState.hintsUsed;
    const hintCounter = document.getElementById('hintCounter');
    
    if (gameState.gameSettings.max_hints === 999) {
        hintCounter.textContent = '(∞)';
    } else {
        hintCounter.textContent = `(${hintsRemaining})`;
        if (hintsRemaining <= 0) {
            document.getElementById('hintBtn').disabled = true;
        }
    }
}

function updateUndoButton() {
    if (gameState.selectedDifficulty === 'medium') {
        const undosRemaining = 5 - gameState.undosUsed;
        document.getElementById('undoCounter').textContent = `(${undosRemaining})`;
        if (undosRemaining <= 0) {
            document.getElementById('undoBtn').disabled = true;
        }
    }
}

function updateMoveStatus(action, row, col, conflicts) {
    const status = document.getElementById('moveStatus');
    if (!status) return;
    
    const actionText = action === 'place' ? 'Placed' : 'Removed';
    
    if (conflicts && conflicts.length > 0) {
        status.textContent = `${actionText} queen at (${row}, ${col}) - ${conflicts.length} conflict(s)!`;
        status.style.color = '#ff6b6b';
    } else {
        status.textContent = `${actionText} queen at (${row}, ${col}) - Valid move!`;
        status.style.color = '#51cf66';
    }
}

// =============================================
// UTILITY FUNCTIONS
// =============================================

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
