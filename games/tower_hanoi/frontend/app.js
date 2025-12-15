/**
 * Tower of Hanoi Interactive Game - Frontend Application
 * Manages UI interactions, API calls, and game visualization
 */

class TowerOfHanoiApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.currentRound = null;
        this.algorithmChart = null;
        this.statsChart = null;
        
        // Gameplay visualization properties
        this.gameState = {
            towers: [],
            diskCount: 0,
            pegCount: 0,
            moveSequence: [],
            currentMoveIndex: 0,
            isAnimating: false,
            animationSpeed: 500
        };
        
        // Track manual play moves
        this.manualMoveSequence = [];
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.showSection('homeSection');
        await this.loadLeaderboard();
        await this.loadAlgorithmStats();
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('homeBtn').addEventListener('click', () => this.showSection('homeSection'));
        document.getElementById('playBtn').addEventListener('click', () => this.showSection('playSection'));
        document.getElementById('leaderboardBtn').addEventListener('click', () => {
            this.showSection('leaderboardSection');
            this.loadLeaderboard();
        });
        document.getElementById('aboutBtn').addEventListener('click', () => this.showSection('aboutSection'));

        // Hero buttons
        document.getElementById('startGameBtn')?.addEventListener('click', () => this.showSection('playSection'));
        document.getElementById('viewLeaderboardBtn').addEventListener('click', () => {
            this.showSection('leaderboardSection');
            this.loadLeaderboard();
        });

        // Play section controls
        document.getElementById('startPlayBtn').addEventListener('click', () => this.startInteractivePlay());
        
        // Visualization controls
        document.getElementById('playAnimationBtn')?.addEventListener('click', () => this.playAnimation());
        document.getElementById('pauseAnimationBtn')?.addEventListener('click', () => this.pauseAnimation());
        document.getElementById('resetVisualizationBtn')?.addEventListener('click', () => this.resetVisualization());
        document.getElementById('animationSpeed')?.addEventListener('input', (e) => {
            this.gameState.animationSpeed = parseInt(e.target.value);
            document.getElementById('speedValue').textContent = `${e.target.value}ms`;
        });

        // Game controls (legacy - if needed)
        document.getElementById('createRoundBtn')?.addEventListener('click', () => this.createRound());
        
        // Disk count preview
        document.getElementById('diskCountSelect')?.addEventListener('change', () => this.updateDiskPreview());
        document.getElementById('pegCount')?.addEventListener('change', () => this.updateDiskPreview());

        // Refresh buttons
        document.getElementById('refreshLeaderboardBtn').addEventListener('click', () => this.loadLeaderboard());
        document.getElementById('refreshStatsBtn')?.addEventListener('click', () => this.loadAlgorithmStats());
        
        // Algorithm filter
        document.getElementById('algorithmFilter').addEventListener('click', () => this.filterLeaderboard());
    }

    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        document.getElementById(sectionId).classList.add('active');

        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        const buttonMap = {
            'homeSection': 'homeBtn',
            'playSection': 'playBtn',
            'leaderboardSection': 'leaderboardBtn',
            'algorithmsSection': 'algorithmsBtn',
            'aboutSection': 'aboutBtn'
        };

        if (buttonMap[sectionId]) {
            document.getElementById(buttonMap[sectionId]).classList.add('active');
        }
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        console.log(`API Call: ${method} ${this.apiBaseUrl}${endpoint}`, data);
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, options);
            console.log('API Response:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error Response:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            console.log('API Result:', result);
            return result;
        } catch (error) {
            console.error('API Error:', error);
            this.showNotification(`API Error: ${error.message}`, 'error');
            throw error;
        }
    }

    async createRound() {
        console.log('createRound called');
        try {
            this.showLoading();
            
            const pegCountEl = document.getElementById('pegCount');
            const diskCountEl = document.getElementById('diskCountSelect');
            
            if (!pegCountEl || !diskCountEl) {
                throw new Error('Form elements not found');
            }
            
            const pegCount = parseInt(pegCountEl.value);
            const diskCountSelect = diskCountEl.value;
            
            console.log('Form values:', { pegCount, diskCountSelect });
            
            // Generate random number of disks between 5 and 10 if not specified
            const randomDisks = Math.floor(Math.random() * 6) + 5; // Random number from 5 to 10
            
            // Backend expects n_disks and peg_count
            const requestData = {
                peg_count: pegCount,
                n_disks: diskCountSelect ? parseInt(diskCountSelect) : randomDisks
            };
            
            console.log('Request data:', requestData);
            
            // Test basic connectivity first
            try {
                const healthResponse = await fetch(`${this.apiBaseUrl.replace('/api', '')}/api/health`);
                console.log('Health check:', healthResponse.status);
            } catch (healthError) {
                throw new Error('Cannot connect to server. Please check if the backend is running.');
            }
            
            const roundData = await this.apiCall('/rounds', 'POST', requestData);
            console.log('Round created:', roundData);
            
            this.currentRound = roundData;
            
            // Only call displayRoundInfo if we have the elements
            try {
                this.displayRoundInfo(roundData);
            } catch (displayError) {
                console.warn('Could not display round info:', displayError);
            }
            
            // Show round info section
            const roundInfoEl = document.getElementById('roundInfo');
            if (roundInfoEl) {
                roundInfoEl.style.display = 'block';
            }
            
            // Initialize interactive game with the created round parameters
            const gameContainer = document.getElementById('interactiveGameContainer');
            if (gameContainer) {
                try {
                    // Clear any existing game
                    if (window.interactiveGame) {
                        console.log('Clearing existing interactive game');
                    }
                    window.interactiveGame = new InteractiveTowerGame(gameContainer, roundData.n_disks, roundData.peg_count);
                    console.log('Interactive game initialized with', roundData.n_disks, 'disks and', roundData.peg_count, 'pegs');
                } catch (gameError) {
                    console.error('Error initializing interactive game:', gameError);
                    // Don't throw here, just warn
                    this.showNotification('Round created but interactive game failed to load.', 'warning');
                }
            } else {
                console.warn('Interactive game container not found');
            }
            
            // Show success notification
            this.showNotification('Round created successfully! You can now play the interactive game.', 'success');
            
            // Load algorithm results (may take a moment to complete)
            if (roundData.id) {
                setTimeout(() => {
                    try {
                        this.loadAlgorithmResults(roundData.id);
                    } catch (algoError) {
                        console.warn('Could not load algorithm results:', algoError);
                    }
                }, 2000);
            }
            
        } catch (error) {
            console.error('Detailed error in createRound:', error);
            console.error('Error stack:', error.stack);
            this.showNotification(`Failed to create round: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayRoundInfo(round) {
        const roundIdEl = document.getElementById('roundId');
        const diskCountEl = document.getElementById('diskCount');
        const pegCountEl = document.getElementById('pegCountDisplay');
        const minMovesEl = document.getElementById('minMoves');
        
        if (roundIdEl) roundIdEl.textContent = round.id;
        if (diskCountEl) diskCountEl.textContent = round.n_disks;
        if (pegCountEl) pegCountEl.textContent = round.peg_count;
        
        // Calculate minimum moves for 3-peg (2^n - 1)
        const minMoves = Math.pow(2, round.n_disks) - 1;
        if (minMovesEl) minMovesEl.textContent = minMoves;
    }

    visualizeGameState(nDisks, pegCount) {
        const container = document.getElementById('gameVisualization');
        if (!container) {
            console.warn('gameVisualization container not found');
            return;
        }
        container.innerHTML = '';

        const pegs = pegCount === 3 ? ['A', 'B', 'C'] : ['A', 'B', 'C', 'D'];
        
        pegs.forEach((pegLabel, index) => {
            const pegDiv = document.createElement('div');
            pegDiv.className = 'peg';
            
            const label = document.createElement('div');
            label.className = 'peg-label';
            label.textContent = pegLabel;
            
            const rod = document.createElement('div');
            rod.className = 'peg-rod';
            
            pegDiv.appendChild(label);
            pegDiv.appendChild(rod);

            // Add disks to source peg (A)
            if (index === 0) {
                for (let i = nDisks; i >= 1; i--) {
                    const disk = document.createElement('div');
                    disk.className = 'disk';
                    disk.textContent = i;
                    disk.style.width = `${30 + i * 20}px`;
                    disk.style.backgroundColor = this.getDiskColor(i, nDisks);
                    pegDiv.appendChild(disk);
                }
            }

            container.appendChild(pegDiv);
        });
    }

    getDiskColor(diskNumber, totalDisks) {
        const colors = [
            '#ef4444', '#f97316', '#f59e0b', '#eab308', 
            '#84cc16', '#22c55e', '#06b6d4', '#3b82f6', 
            '#6366f1', '#8b5cf6', '#d946ef', '#ec4899'
        ];
        return colors[diskNumber - 1] || colors[colors.length - 1];
    }

    async validateSolution() {
        const formData = this.getFormData();
        if (!formData) return;

        try {
            this.showLoading();
            
            const result = await this.apiCall('/validate', 'POST', {
                n_disks: this.currentRound.n_disks,
                peg_count: this.currentRound.peg_count,
                move_sequence: formData.moveSequence,
                declared_moves: formData.declaredMoves
            });

            this.displayValidationResults(result, false);
            
        } catch (error) {
            console.error('Error validating solution:', error);
        } finally {
            this.hideLoading();
        }
    }

    async submitSolution(event) {
        event.preventDefault();
        
        if (!this.currentRound) {
            this.showError('Please create a round first');
            return;
        }

        const formData = this.getFormData();
        if (!formData) return;

        try {
            this.showLoading();
            
            const result = await this.apiCall(`/rounds/${this.currentRound.id}/submit`, 'POST', formData);
            
            this.displayValidationResults(result.validation_details, true, result);
            
            if (result.correct) {
                this.showSuccess('🎉 Congratulations! Your solution is correct!');
                
                // Refresh leaderboard
                await this.loadLeaderboard();
                
                // Load algorithm comparison
                await this.loadAlgorithmResults(this.currentRound.id);
            }
            
        } catch (error) {
            console.error('Error submitting solution:', error);
        } finally {
            this.hideLoading();
        }
    }

    getFormData() {
        const playerName = document.getElementById('playerName').value.trim();
        const declaredMoves = parseInt(document.getElementById('declaredMoves').value);
        const moveSequenceText = document.getElementById('moveSequence').value.trim();

        if (!playerName || !declaredMoves || !moveSequenceText) {
            this.showError('Please fill in all fields');
            return null;
        }

        // Parse move sequence
        const moveSequence = this.parseMoveSequence(moveSequenceText);
        if (moveSequence.length === 0) {
            this.showError('Please provide a valid move sequence');
            return null;
        }

        return {
            player_name: playerName,
            declared_moves: declaredMoves,
            move_sequence: moveSequence
        };
    }

    parseMoveSequence(moveString) {
        if (!moveString) return [];
        
        // Replace common separators with commas
        const cleanedString = moveString
            .replace(/\n/g, ',')
            .replace(/\r/g, ',')
            .replace(/;/g, ',')
            .replace(/\s+/g, ' ');
        
        // Split by comma and clean up
        let moves = cleanedString.split(',').map(move => move.trim()).filter(move => move);
        
        // If no commas found, try splitting by spaces
        if (moves.length === 1 && moves[0].includes(' ')) {
            moves = moves[0].split(/\s+/).filter(move => move);
        }
        
        return moves;
    }

    displayValidationResults(result, isSubmission = false, submissionResult = null) {
        const container = document.getElementById('validationResults');
        container.innerHTML = '';
        container.style.display = 'block';

        const card = document.createElement('div');
        card.className = 'validation-results';

        if (result.is_valid) {
            card.classList.add('validation-success');
            card.innerHTML = `
                <h3><i class="fas fa-check-circle"></i> ${isSubmission ? 'Solution Accepted!' : 'Validation Successful!'}</h3>
                <div class="validation-details">
                    <p><strong>✅ Move sequence is valid</strong></p>
                    <p><strong>✅ Puzzle completed successfully</strong></p>
                    <p><strong>Total moves:</strong> ${result.total_moves}</p>
                    ${result.declared_moves_message ? `<p><strong>Declared moves:</strong> ${result.declared_moves_message}</p>` : ''}
                    ${submissionResult ? `<p><strong>Submission ID:</strong> ${submissionResult.saved_submission_id}</p>` : ''}
                </div>
            `;
        } else {
            card.classList.add('validation-error');
            card.innerHTML = `
                <h3><i class="fas fa-exclamation-triangle"></i> Validation Failed</h3>
                <div class="validation-details">
                    <p><strong>❌ Found ${result.error_count} error(s)</strong></p>
                    <p><strong>Total moves:</strong> ${result.total_moves}</p>
                    <p><strong>Puzzle completed:</strong> ${result.puzzle_completed ? 'Yes' : 'No'}</p>
                    ${result.declared_moves_message ? `<p><strong>Declared moves:</strong> ${result.declared_moves_message}</p>` : ''}
                    <div class="error-details">
                        <h4>Error Details:</h4>
                        <pre>${result.detailed_report}</pre>
                    </div>
                </div>
            `;
        }

        container.appendChild(card);
    }

    async loadAlgorithmResults(roundId) {
        try {
            const results = await this.apiCall(`/rounds/${roundId}/algorithm-runs`);
            
            if (results.length > 0) {
                this.displayAlgorithmComparison(results);
            }
        } catch (error) {
            console.error('Error loading algorithm results:', error);
        }
    }

    displayAlgorithmComparison(results) {
        const container = document.getElementById('algorithmComparison');
        const resultsContainer = document.getElementById('algorithmResults');
        
        resultsContainer.innerHTML = '';
        
        results.forEach(result => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'algorithm-result';
            resultDiv.innerHTML = `
                <div class="algorithm-name">${result.algorithm_name}</div>
                <div class="algorithm-stats">
                    <span><strong>Moves:</strong> ${result.computed_moves}</span>
                    <span><strong>Runtime:</strong> ${result.runtime_ms.toFixed(3)}ms</span>
                </div>
            `;
            resultsContainer.appendChild(resultDiv);
        });
        
        // Create chart
        this.createAlgorithmChart(results);
        
        container.style.display = 'block';
    }

    createAlgorithmChart(results) {
        const ctx = document.getElementById('algorithmChart').getContext('2d');
        
        if (this.algorithmChart) {
            this.algorithmChart.destroy();
        }
        
        const labels = results.map(r => r.algorithm_name);
        const moves = results.map(r => r.computed_moves);
        const runtimes = results.map(r => r.runtime_ms);
        
        this.algorithmChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Number of Moves',
                        data: moves,
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Runtime (ms)',
                        data: runtimes,
                        backgroundColor: 'rgba(239, 68, 68, 0.6)',
                        borderColor: 'rgba(239, 68, 68, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1',
                        type: 'line'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Algorithm Performance Comparison'
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Number of Moves'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Runtime (ms)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    async loadLeaderboard() {
        try {
            const leaderboard = await this.apiCall('/leaderboard?limit=200');
            this.fullLeaderboard = leaderboard; // Store full data
            this.displayLeaderboard(leaderboard);
        } catch (error) {
            console.error('Error loading leaderboard:', error);
        }
    }
    
    filterLeaderboard() {
        const filter = document.getElementById('algorithmFilter').value;
        let filtered = this.fullLeaderboard || [];
        
        if (filter !== 'all') {
            filtered = filtered.filter(player => player.algorithm_type === filter);
        }
        
        this.displayLeaderboard(filtered);
    }

    displayLeaderboard(leaderboard) {
        const container = document.getElementById('leaderboardTable');
        
        if (leaderboard.length === 0) {
            container.innerHTML = '<p class="text-center">No players yet. Be the first to submit a solution!</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.className = 'table';
        
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th>Algorithm</th>
                    <th>Config</th>
                    <th>Best Moves</th>
                    <th>Avg Moves</th>
                    <th>Correct</th>
                    <th>Total</th>
                    <th>Last Submission</th>
                </tr>
            </thead>
            <tbody>
                ${leaderboard.map((player, index) => {
                    const algorithmDisplay = player.algorithm_type 
                        ? player.algorithm_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
                        : '-';
                    const configDisplay = player.disk_count && player.peg_count
                        ? `${player.disk_count}D/${player.peg_count}P`
                        : '-';
                    
                    return `
                        <tr>
                            <td class="rank">#${index + 1}</td>
                            <td>${player.name}</td>
                            <td><span class="badge badge-info">${algorithmDisplay}</span></td>
                            <td><span class="badge badge-secondary">${configDisplay}</span></td>
                            <td>${player.best_moves || '-'}</td>
                            <td>${player.avg_moves ? player.avg_moves.toFixed(1) : '-'}</td>
                            <td>${player.correct_submissions}</td>
                            <td>${player.total_submissions}</td>
                            <td>${player.last_submission ? new Date(player.last_submission).toLocaleDateString() : '-'}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        `;
        
        container.innerHTML = '';
        container.appendChild(table);
    }

    async loadAlgorithmStats() {
        try {
            const [algorithmStats, roundStats] = await Promise.all([
                this.apiCall('/stats/algorithms'),
                this.apiCall('/stats/rounds')
            ]);
            
            this.displayAlgorithmStats(algorithmStats);
            this.displayRoundStats(roundStats);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    displayAlgorithmStats(stats) {
        const ctx = document.getElementById('algorithmStatsChart').getContext('2d');
        
        if (this.statsChart) {
            this.statsChart.destroy();
        }
        
        if (stats.length === 0) {
            return;
        }
        
        const threePegStats = stats.filter(s => s.peg_count === 3);
        const fourPegStats = stats.filter(s => s.peg_count === 4);
        
        const labels = [...new Set(stats.map(s => s.algorithm_name))];
        
        this.statsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Avg Moves (3-peg)',
                        data: labels.map(label => {
                            const stat = threePegStats.find(s => s.algorithm_name === label);
                            return stat ? stat.avg_moves : 0;
                        }),
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Avg Moves (4-peg)',
                        data: labels.map(label => {
                            const stat = fourPegStats.find(s => s.algorithm_name === label);
                            return stat ? stat.avg_moves : 0;
                        }),
                        backgroundColor: 'rgba(239, 68, 68, 0.6)',
                        borderColor: 'rgba(239, 68, 68, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Algorithm Performance Statistics'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Average Moves'
                        }
                    }
                }
            }
        });
    }

    displayRoundStats(stats) {
        const container = document.getElementById('roundStats');
        container.innerHTML = '';
        
        stats.forEach(stat => {
            const statDiv = document.createElement('div');
            statDiv.className = 'stat-item';
            statDiv.innerHTML = `
                <div class="stat-label">${stat.n_disks} disks, ${stat.peg_count} pegs</div>
                <div class="stat-value">
                    ${stat.total_rounds} rounds, 
                    ${stat.correct_submissions}/${stat.total_submissions} solutions
                    ${stat.best_winning_moves ? `, best: ${stat.best_winning_moves}` : ''}
                </div>
            `;
            container.appendChild(statDiv);
        });
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        // Set colors based on type
        if (type === 'error') {
            notification.style.backgroundColor = '#fef2f2';
            notification.style.borderLeft = '4px solid #ef4444';
            notification.style.color = '#dc2626';
        } else if (type === 'success') {
            notification.style.backgroundColor = '#ecfdf5';
            notification.style.borderLeft = '4px solid #10b981';
            notification.style.color = '#047857';
        } else {
            notification.style.backgroundColor = '#eff6ff';
            notification.style.borderLeft = '4px solid #3b82f6';
            notification.style.color = '#1e40af';
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    updateDiskPreview() {
        const diskCountSelect = document.getElementById('diskCountSelect');
        const pegCount = parseInt(document.getElementById('pegCount').value);
        const selectedDisks = diskCountSelect.value;
        
        if (selectedDisks) {
            const diskCount = parseInt(selectedDisks);
            this.visualizeGameState(diskCount, pegCount, true);
        } else {
            // Show preview with random disk count (7 as example, range is 5-10)
            this.visualizeGameState(7, pegCount, true);
        }
    }

    visualizeGameState(diskCount, pegCount, isPreview = false) {
        const container = document.getElementById('gameVisualization');
        container.innerHTML = '';
        
        // Create pegs
        const pegsContainer = document.createElement('div');
        pegsContainer.className = 'pegs-display';
        pegsContainer.style.cssText = `
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            padding: 20px;
            min-height: ${Math.max(150, diskCount * 25 + 80)}px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            margin: 20px 0;
            position: relative;
        `;

        const pegLabels = pegCount === 3 ? ['A', 'B', 'C'] : ['A', 'B', 'C', 'D'];
        
        pegLabels.forEach((label, index) => {
            const peg = document.createElement('div');
            peg.className = `peg peg-${label}`;
            peg.style.cssText = `
                display: flex;
                flex-direction: column;
                align-items: center;
                position: relative;
                width: 120px;
            `;

            // Peg base
            const base = document.createElement('div');
            base.style.cssText = `
                width: 100px;
                height: 10px;
                background: #8B4513;
                border-radius: 5px;
                position: relative;
            `;

            // Peg rod
            const rod = document.createElement('div');
            rod.style.cssText = `
                width: 6px;
                height: ${diskCount * 25 + 50}px;
                background: #8B4513;
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                border-radius: 3px;
            `;

            // Peg label
            const labelEl = document.createElement('div');
            labelEl.textContent = label;
            labelEl.style.cssText = `
                font-weight: bold;
                font-size: 18px;
                color: #333;
                margin-top: 10px;
            `;

            // Add disks to first peg (source)
            if (index === 0) {
                for (let i = diskCount; i >= 1; i--) {
                    const disk = document.createElement('div');
                    const width = 30 + i * 8;
                    const hue = (i * 360) / diskCount;
                    
                    disk.style.cssText = `
                        width: ${width}px;
                        height: 20px;
                        background: hsl(${hue}, 70%, 60%);
                        border: 2px solid hsl(${hue}, 70%, 40%);
                        border-radius: 10px;
                        position: absolute;
                        bottom: ${10 + (diskCount - i) * 25}px;
                        left: 50%;
                        transform: translateX(-50%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        font-size: 12px;
                        text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        z-index: ${i};
                    `;
                    disk.textContent = i;
                    base.appendChild(disk);
                }
            }

            base.appendChild(rod);
            peg.appendChild(base);
            peg.appendChild(labelEl);
            pegsContainer.appendChild(peg);
        });

        container.appendChild(pegsContainer);

        // Add preview notice if this is a preview
        if (isPreview) {
            const notice = document.createElement('div');
            notice.textContent = '👆 Preview - Create round to start playing!';
            notice.style.cssText = `
                text-align: center;
                color: #666;
                font-style: italic;
                margin-top: 10px;
            `;
            container.appendChild(notice);
        }
    }

    // ===== GAME VISUALIZATION METHODS =====
    
    initializeGameVisualization(diskCount, pegCount) {
        this.gameState.diskCount = diskCount;
        this.gameState.pegCount = pegCount;
        this.gameState.towers = Array(pegCount).fill().map(() => []);
        
        // Initialize first tower with all disks (largest to smallest)
        for (let i = diskCount; i >= 1; i--) {
            this.gameState.towers[0].push(i);
        }
        
        // Show visualization board
        document.getElementById('visualGameBoard').style.display = 'block';
        
        // Clear previous content
        const towerDisplay = document.getElementById('towerDisplay');
        towerDisplay.innerHTML = '';
        
        // Initialize interactive game for manual play
        if (this.currentPlay && !this.currentPlay.isAutoCompleted) {
            // Create interactive game container
            const interactiveContainer = document.createElement('div');
            interactiveContainer.id = 'interactiveGameContainer';
            towerDisplay.appendChild(interactiveContainer);
            
            // Initialize interactive game with drag-and-drop
            if (window.interactiveGame) {
                window.interactiveGame = null;
            }
            window.interactiveGame = new InteractiveTowerGame(
                interactiveContainer, 
                diskCount, 
                pegCount
            );
            
            // Auto-start the game with current player info
            window.interactiveGame.playerName = this.currentPlay.playerName;
            window.interactiveGame.gameActive = true;
            window.interactiveGame.startTime = new Date();
            window.interactiveGame.drawTowers();
            window.interactiveGame.startTimer();
        } else {
            // Show static towers for animation
            this.renderTowers();
        }
    }
    
    renderTowers() {
        const towerDisplay = document.getElementById('towerDisplay');
        if (!towerDisplay) return;
        
        towerDisplay.innerHTML = '';
        
        const pegLabels = ['A', 'B', 'C', 'D'];
        
        for (let i = 0; i < this.gameState.pegCount; i++) {
            const towerContainer = document.createElement('div');
            towerContainer.className = 'tower-container';
            towerContainer.dataset.tower = i;
            
            // Tower label
            const label = document.createElement('div');
            label.className = 'tower-label';
            label.textContent = `Tower ${pegLabels[i]}`;
            towerContainer.appendChild(label);
            
            // Tower pole
            const pole = document.createElement('div');
            pole.className = 'tower-pole';
            
            // Disks container
            const disksContainer = document.createElement('div');
            disksContainer.className = 'tower-disks';
            
            // Render disks on this tower
            const disks = this.gameState.towers[i];
            disks.forEach((diskSize, index) => {
                const disk = document.createElement('div');
                disk.className = `disk disk-${diskSize}`;
                disk.textContent = diskSize;
                disk.dataset.size = diskSize;
                disksContainer.appendChild(disk);
            });
            
            pole.appendChild(disksContainer);
            towerContainer.appendChild(pole);
            
            // Tower base
            const base = document.createElement('div');
            base.className = 'tower-base';
            towerContainer.appendChild(base);
            
            towerDisplay.appendChild(towerContainer);
        }
    }
    
    async animateMove(fromTower, toTower) {
        return new Promise((resolve) => {
            // Get the disk to move
            const disk = this.gameState.towers[fromTower].pop();
            
            // Add moving animation class
            const towerElements = document.querySelectorAll('.tower-container');
            const fromElement = towerElements[fromTower];
            const diskElements = fromElement.querySelectorAll('.disk');
            const movingDisk = diskElements[diskElements.length - 1];
            
            if (movingDisk) {
                movingDisk.classList.add('moving');
            }
            
            // Wait for animation
            setTimeout(() => {
                // Move disk to destination tower
                this.gameState.towers[toTower].push(disk);
                
                // Re-render towers
                this.renderTowers();
                
                // Update move count
                this.gameState.currentMoveIndex++;
                if (this.currentPlay) {
                    this.currentPlay.moveCount++;
                    document.getElementById('movesMade').textContent = this.currentPlay.moveCount;
                }
                
                resolve();
            }, this.gameState.animationSpeed);
        });
    }
    
    async playAnimation() {
        if (!this.gameState.moveSequence || this.gameState.moveSequence.length === 0) {
            this.showNotification('No moves to animate', 'warning');
            return;
        }
        
        // Reset to initial state if starting from beginning
        if (this.gameState.currentMoveIndex === 0) {
            this.gameState.towers = Array(this.gameState.pegCount).fill().map(() => []);
            for (let i = this.gameState.diskCount; i >= 1; i--) {
                this.gameState.towers[0].push(i);
            }
            this.renderTowers();
        }
        
        this.gameState.isAnimating = true;
        document.getElementById('playAnimationBtn').style.display = 'none';
        document.getElementById('pauseAnimationBtn').style.display = 'inline-block';
        
        while (this.gameState.currentMoveIndex < this.gameState.moveSequence.length && this.gameState.isAnimating) {
            const move = this.gameState.moveSequence[this.gameState.currentMoveIndex];
            const [from, to] = this.parseMoveString(move);
            
            await this.animateMove(from, to);
        }
        
        this.gameState.isAnimating = false;
        document.getElementById('playAnimationBtn').style.display = 'inline-block';
        document.getElementById('pauseAnimationBtn').style.display = 'none';
        
        if (this.gameState.currentMoveIndex >= this.gameState.moveSequence.length) {
            this.showNotification('Animation complete!', 'success');
        }
    }
    
    pauseAnimation() {
        this.gameState.isAnimating = false;
        document.getElementById('playAnimationBtn').style.display = 'inline-block';
        document.getElementById('pauseAnimationBtn').style.display = 'none';
    }
    
    resetVisualization() {
        this.gameState.currentMoveIndex = 0;
        this.initializeGameVisualization(this.gameState.diskCount, this.gameState.pegCount);
        this.showNotification('Visualization reset', 'success');
    }
    
    parseMoveString(move) {
        // Parse move string like "A->B" to tower indices
        const pegLabels = ['A', 'B', 'C', 'D'];
        const [fromLabel, toLabel] = move.split('->');
        return [pegLabels.indexOf(fromLabel), pegLabels.indexOf(toLabel)];
    }

    // ===== NEW GAMEPLAY METHODS =====
    
    async startInteractivePlay() {
        const playerName = document.getElementById('playPlayerName').value.trim();
        const diskCountValue = document.getElementById('playDiskCount').value;
        // Handle random disk selection (5-10)
        const diskCount = diskCountValue === 'random' 
            ? Math.floor(Math.random() * 6) + 5  // Random number between 5 and 10
            : parseInt(diskCountValue);
        const pegCount = parseInt(document.getElementById('playPegCount').value);
        
        // Auto-select algorithm based on peg count - backend will determine recursive/iterative
        const algorithmName = pegCount === 3 ? 'Auto 3-Peg' : 'Auto 4-Peg';
        
        if (!playerName) {
            this.showNotification('Please enter your name', 'error');
            return;
        }
        
        // Store game settings
        this.currentPlay = {
            playerName,
            diskCount,
            pegCount,
            algorithmName,
            startTime: Date.now(),
            moves: [],
            moveCount: 0
        };
        
        // Reset manual move tracking
        this.manualMoveSequence = [];
        
        // Initialize game visualization
        this.initializeGameVisualization(diskCount, pegCount);
        
        // Show game info and controls
        document.getElementById('playGameInfo').style.display = 'block';
        document.getElementById('currentAlgorithm').textContent = algorithmName;
        document.getElementById('optimalMoves').textContent = this.calculateOptimalMoves(diskCount, pegCount);
        
        // Start timer
        this.playTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.currentPlay.startTime) / 1000);
            document.getElementById('timeElapsed').textContent = `${elapsed}s`;
        }, 1000);
        
        this.showNotification(`Game started! Good luck, ${playerName}!`, 'success');
    }
    
    calculateOptimalMoves(diskCount, pegCount) {
        if (pegCount === 3) {
            return Math.pow(2, diskCount) - 1;
        } else {
            // 4-peg optimal calculation
            let dp = [0, 1, 3];
            for (let i = 3; i <= diskCount; i++) {
                let min = Infinity;
                for (let k = 1; k < i; k++) {
                    const moves = 2 * dp[k] + (Math.pow(2, i - k) - 1);
                    min = Math.min(min, moves);
                }
                dp[i] = min;
            }
            return dp[diskCount];
        }
    }
    
    async autoCompleteGame() {
        if (!this.currentPlay) {
            this.showNotification('No game in progress', 'error');
            return;
        }
        
        try {
            this.showLoading();
            
            // Use default recursive algorithm for auto-complete
            const algorithmName = this.currentPlay.pegCount === 3 ? 'Recursive 3-Peg' : 'Recursive 4-Peg';
            
            const response = await this.apiCall('/gameplay/auto-complete', 'POST', {
                disk_count: this.currentPlay.diskCount,
                peg_count: this.currentPlay.pegCount,
                algorithm_name: algorithmName
            });
            
            // Store the solution
            this.currentPlay.solution = response;
            this.currentPlay.moveCount = response.move_count;
            this.currentPlay.algorithmExecutionTimeMs = response.execution_time_ms;
            this.currentPlay.moves = response.move_sequence;
            this.currentPlay.isAutoCompleted = true;
            
            this.hideLoading();
            
            // Animate the solution in the interactive game
            if (window.interactiveGame) {
                this.showNotification('Auto-solving the game... Watch the moves!', 'success');
                await this.animateInteractiveSolution(response.move_sequence);
            } else {
                // Fallback to static animation if interactive game not available
                const towerDisplay = document.getElementById('towerDisplay');
                towerDisplay.innerHTML = '';
                this.renderTowers();
                
                // Set up animation
                this.gameState.moveSequence = response.move_sequence;
                this.gameState.currentMoveIndex = 0;
                
                // Show animation controls
                document.getElementById('playAnimationBtn').style.display = 'inline-block';
                document.getElementById('resetVisualizationBtn').style.display = 'inline-block';
                document.getElementById('animationSpeedControl').style.display = 'flex';
                
                // Update UI
                document.getElementById('movesMade').textContent = response.move_count;
                
                // Show results
                this.displayPlayResults();
                
                this.showNotification('Game auto-completed! Click "Play Animation" to visualize the solution', 'success');
            }
            
        } catch (error) {
            this.hideLoading();
            this.showNotification(`Failed to auto-complete: ${error.message}`, 'error');
        }
    }
    
    async animateInteractiveSolution(moveSequence) {
        const delay = 800; // 800ms between moves
        
        for (const move of moveSequence) {
            // Parse move like "A->B"
            const pegLabels = ['A', 'B', 'C', 'D'];
            const [fromLabel, toLabel] = move.split('->');
            const fromPeg = pegLabels.indexOf(fromLabel);
            const toPeg = pegLabels.indexOf(toLabel);
            
            // Execute the move in the interactive game
            if (window.interactiveGame && fromPeg !== -1 && toPeg !== -1) {
                window.interactiveGame.makeMove(fromPeg, toPeg);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        
        // Show results after animation completes
        this.displayPlayResults();
        this.showNotification('Auto-solve complete! Click "Save Game" to save your result.', 'success');
    }
    
    async saveGameplaySession() {
        if (!this.currentPlay || !this.currentPlay.solution) {
            this.showNotification('Please complete or auto-complete the game first', 'error');
            return;
        }
        
        try {
            this.showLoading();
            
            const gameplayTimeMs = Date.now() - this.currentPlay.startTime;
            
            const response = await this.apiCall('/gameplay/save', 'POST', {
                player_name: this.currentPlay.playerName,
                algorithm_name: this.currentPlay.algorithmName,
                disk_count: this.currentPlay.diskCount,
                peg_count: this.currentPlay.pegCount,
                move_count: this.currentPlay.moveCount,
                algorithm_execution_time_ms: this.currentPlay.algorithmExecutionTimeMs,
                gameplay_time_ms: gameplayTimeMs,
                generated_sequence: this.currentPlay.moves,
                is_auto_completed: this.currentPlay.isAutoCompleted || false
            });
            
            this.hideLoading();
            this.showNotification(`Game saved successfully! Session ID: ${response.id}`, 'success');
            
            // Stop timer
            if (this.playTimer) {
                clearInterval(this.playTimer);
                this.playTimer = null;
            }
            
            // Reset for new game
            setTimeout(() => {
                this.resetPlaySection();
            }, 2000);
            
        } catch (error) {
            this.hideLoading();
            this.showNotification(`Failed to save game: ${error.message}`, 'error');
        }
    }
    
    displayPlayResults() {
        const resultsDiv = document.getElementById('playResultsDiv');
        const resultsContent = document.getElementById('playResultsContent');
        
        if (!this.currentPlay || !this.currentPlay.solution) {
            return;
        }
        
        const optimalMoves = this.calculateOptimalMoves(this.currentPlay.diskCount, this.currentPlay.pegCount);
        const efficiency = ((optimalMoves / this.currentPlay.moveCount) * 100).toFixed(1);
        
        resultsContent.innerHTML = `
            <div class="results-stats">
                <div class="stat-card">
                    <div class="stat-label">Total Moves</div>
                    <div class="stat-value">${this.currentPlay.moveCount}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Optimal Moves</div>
                    <div class="stat-value">${optimalMoves}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Efficiency</div>
                    <div class="stat-value">${efficiency}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Execution Time</div>
                    <div class="stat-value">${this.currentPlay.algorithmExecutionTimeMs.toFixed(3)}ms</div>
                </div>
            </div>
            <div class="move-sequence">
                <h4>Move Sequence:</h4>
                <div class="sequence-container">
                    ${this.currentPlay.moves.map((move, i) => 
                        `<span class="move-item">${i + 1}. ${move}</span>`
                    ).join('')}
                </div>
            </div>
        `;
        
        resultsDiv.style.display = 'block';
    }
    
    resetPlaySection() {
        document.getElementById('playPlayerName').value = '';
        document.getElementById('playGameInfo').style.display = 'none';
        document.getElementById('playResultsDiv').style.display = 'none';
        document.getElementById('movesMade').textContent = '0';
        document.getElementById('timeElapsed').textContent = '0s';
        
        if (this.playTimer) {
            clearInterval(this.playTimer);
            this.playTimer = null;
        }
        
        this.currentPlay = null;
    }
}

/**
 * Interactive Tower of Hanoi Game Class
 * Handles visual gameplay with click-to-move functionality
 */
class InteractiveTowerGame {
    constructor(container, diskCount = 3, pegCount = 3) {
        if (!container) {
            throw new Error('Container element is required for InteractiveTowerGame');
        }
        
        this.container = container;
        this.diskCount = diskCount;
        this.pegCount = pegCount;
        this.towers = Array(pegCount).fill().map(() => []);
        this.selectedDisk = null;
        this.selectedPeg = null;
        this.moves = 0;
        this.startTime = null;
        this.gameActive = false;
        this.playerName = '';
        
        this.initializeTowers();
        this.setupGameUI();
    }

    initializeTowers() {
        this.towers = Array(this.pegCount).fill().map(() => []);
        // Initialize first peg with disks (largest to smallest)
        for (let i = this.diskCount; i >= 1; i--) {
            this.towers[0].push(i);
        }
        this.moves = 0;
        this.selectedDisk = null;
        this.selectedPeg = null;
    }

    setupGameUI() {
        if (!this.container) {
            console.error('Cannot setup game UI: container is null');
            return;
        }
        
        this.container.innerHTML = `
            <div class="game-status">
                <div id="statusMessage" class="status-message info">
                    🎯 Drag disks between pegs or click to select and move. Get all disks to the rightmost peg!
                </div>
            </div>

            <div class="pegs-container" id="pegsContainer">
                <!-- Towers will be drawn here -->
            </div>
        `;
        
        this.drawTowers();
    }

    startGame() {
        const nameInput = document.getElementById('playerNameInput');
        const pegSelect = document.getElementById('gamePegCount');
        const diskSelect = document.getElementById('gameDiskCount');
        
        if (!nameInput.value.trim()) {
            this.showStatus('Please enter your name!', 'error');
            return;
        }

        this.playerName = nameInput.value.trim();
        this.pegCount = parseInt(pegSelect.value);
        this.diskCount = parseInt(diskSelect.value);
        this.gameActive = true;
        this.startTime = new Date();
        
        this.initializeTowers();
        this.setupGameUI();
        this.startTimer();
        this.showStatus(`Welcome ${this.playerName}! Move all disks to the rightmost peg. Good luck! 🚀`, 'success');
    }

    drawTowers() {
        const pegsContainer = document.getElementById('pegsContainer');
        if (!pegsContainer) return;
        
        pegsContainer.innerHTML = '';
        
        const canvasWidth = pegsContainer.clientWidth || 600;
        const canvasHeight = 300;
        const pegWidth = Math.floor(canvasWidth / this.pegCount) - 10;
        
        for (let i = 0; i < this.pegCount; i++) {
            const pegContainer = document.createElement('div');
            pegContainer.className = 'peg-container';
            pegContainer.dataset.peg = i;
            pegContainer.style.cssText = `
                width: ${pegWidth}px;
                height: ${canvasHeight}px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-end;
                position: relative;
                background: #e5e7eb;
                border-radius: 12px;
                margin: 0 5px;
                padding: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            `;
            
            // Add click handler for peg
            pegContainer.addEventListener('click', () => this.handlePegClick(i));
            
            // Add drag-and-drop handlers for peg
            pegContainer.addEventListener('dragover', (e) => this.handleDragOver(e));
            pegContainer.addEventListener('drop', (e) => this.handleDrop(e, i));
            
            // Add peg rod
            const pegRod = document.createElement('div');
            pegRod.style.cssText = `
                width: 10px;
                height: 80%;
                background: linear-gradient(to bottom, #6b7280, #374151);
                border-radius: 5px;
                position: absolute;
                bottom: 15px;
                z-index: 1;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            `;
            pegContainer.appendChild(pegRod);
            
            // Draw peg base (the platform at the bottom of the stick)
            const pegBase = document.createElement('div');
            pegBase.style.cssText = `
                width: 80px;
                height: 15px;
                background: linear-gradient(to right, #8b7355, #654321, #8b7355);
                border-radius: 8px;
                position: absolute;
                bottom: 15px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1;
                box-shadow: 0 3px 6px rgba(0,0,0,0.4);
            `;
            pegContainer.appendChild(pegBase);
            
            // Add peg label
            const pegLabel = document.createElement('div');
            const isTarget = (i === this.pegCount - 1);
            pegLabel.style.cssText = `
                position: absolute;
                top: 5px;
                left: 50%;
                transform: translateX(-50%);
                background: ${isTarget ? 'rgba(34, 197, 94, 0.9)' : 'rgba(59, 130, 246, 0.8)'};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                z-index: 2;
            `;
            // Label the first peg as Source, last as Target, others as Auxiliary
            if (i === 0) {
                pegLabel.textContent = 'Source';
            } else if (i === this.pegCount - 1) {
                pegLabel.textContent = 'Target';
            } else {
                pegLabel.textContent = 'Auxiliary';
            }
            pegContainer.appendChild(pegLabel);
            
            // Add disks (in reverse order to stack from bottom with column flex-direction)
            const disks = this.towers[i];
            for (let j = disks.length - 1; j >= 0; j--) {
                const diskSize = disks[j];
                const diskElement = document.createElement('div');
                diskElement.className = 'disk';
                diskElement.dataset.size = diskSize;
                diskElement.dataset.peg = i;
                diskElement.dataset.position = j;
                
                const diskWidth = 30 + diskSize * 25;
                diskElement.style.cssText = `
                    width: ${diskWidth}px;
                    height: 25px;
                    background: linear-gradient(45deg, hsl(${diskSize * 45}, 70%, 55%), hsl(${diskSize * 45}, 70%, 45%));
                    border-radius: 12px;
                    margin: 3px 0;
                    border: 3px solid #374151;
                    z-index: ${10 + j};
                    position: relative;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    color: white;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                `;
                diskElement.textContent = diskSize;
                
                // Add click handler for disk
                diskElement.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.handleDiskClick(diskSize, i);
                });
                
                // Add drag-and-drop handlers
                diskElement.draggable = true;
                diskElement.addEventListener('dragstart', (e) => this.handleDragStart(e, diskSize, i));
                diskElement.addEventListener('dragend', (e) => this.handleDragEnd(e));
                
                // Mark top disk as movable
                if (j === disks.length - 1) {
                    diskElement.classList.add('movable');
                }
                
                pegContainer.appendChild(diskElement);
            }
            
            pegsContainer.appendChild(pegContainer);
        }
    }

    handleDragStart(e, diskSize, pegIndex) {
        if (!this.gameActive) return;
        
        const topDisk = this.towers[pegIndex][this.towers[pegIndex].length - 1];
        
        if (topDisk !== diskSize) {
            e.preventDefault();
            this.showStatus('You can only drag the top disk from each peg! 🚫', 'error');
            return;
        }
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('diskSize', diskSize);
        e.dataTransfer.setData('fromPeg', pegIndex);
        
        e.target.style.opacity = '0.5';
        this.selectedDisk = diskSize;
        this.selectedPeg = pegIndex;
        
        this.showStatus(`Dragging disk ${diskSize}... Drop on a valid peg! 🎯`, 'info');
    }
    
    handleDragEnd(e) {
        e.target.style.opacity = '1';
    }
    
    handleDragOver(e) {
        if (!this.gameActive) return;
        
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        
        // Add visual feedback
        e.currentTarget.style.borderColor = '#3b82f6';
        e.currentTarget.style.backgroundColor = '#eff6ff';
    }
    
    handleDrop(e, toPeg) {
        if (!this.gameActive) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        // Reset visual feedback
        e.currentTarget.style.borderColor = 'transparent';
        e.currentTarget.style.backgroundColor = '#e5e7eb';
        
        const diskSize = parseInt(e.dataTransfer.getData('diskSize'));
        const fromPeg = parseInt(e.dataTransfer.getData('fromPeg'));
        
        if (fromPeg === toPeg) {
            this.showStatus('Disk returned to same peg. 🔄', 'info');
            this.selectedDisk = null;
            this.selectedPeg = null;
            return;
        }
        
        // Try to move disk to this peg
        if (this.isValidMove(fromPeg, toPeg)) {
            this.makeMove(fromPeg, toPeg);
            this.selectedDisk = null;
            this.selectedPeg = null;
            this.updateVisualSelection();
        } else {
            this.showStatus('Invalid move! You cannot place a larger disk on a smaller one. ❌', 'error');
            this.selectedDisk = null;
            this.selectedPeg = null;
        }
    }
    
    async autoSaveGameCompletion(duration) {
        if (!window.app || !window.app.currentPlay) {
            console.warn('No active play session to save');
            return;
        }
        
        try {
            const currentPlay = window.app.currentPlay;
            const gameplayTimeMs = Date.now() - currentPlay.startTime;
            
            const gameData = {
                player_name: this.playerName,
                algorithm_name: currentPlay.algorithmName,
                disk_count: this.diskCount,
                peg_count: this.pegCount,
                move_count: this.moves,
                algorithm_execution_time_ms: gameplayTimeMs, // Use gameplay time as execution time for leaderboard
                gameplay_time_ms: gameplayTimeMs,
                generated_sequence: window.app.manualMoveSequence,
                is_auto_completed: false
            };
            
            console.log('Auto-saving completed game:', gameData);
            
            const response = await fetch('http://localhost:8000/api/gameplay/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(gameData)
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Game automatically saved! Session ID:', result.id);
                this.showStatus(`🎉 Game completed and saved automatically! (Session: ${result.id})`, 'success');
            } else {
                console.error('Failed to auto-save game:', response.status);
            }
        } catch (error) {
            console.error('Error auto-saving game:', error);
        }
    }

    handleDiskClick(diskSize, pegIndex) {
        if (!this.gameActive) return;
        
        const topDisk = this.towers[pegIndex][this.towers[pegIndex].length - 1];
        
        if (topDisk !== diskSize) {
            this.showStatus('You can only move the top disk from each peg! 🚫', 'error');
            return;
        }
        
        if (this.selectedDisk === diskSize && this.selectedPeg === pegIndex) {
            // Deselect
            this.selectedDisk = null;
            this.selectedPeg = null;
            this.showStatus('Disk deselected. Choose a disk to move! 👆', 'info');
        } else {
            // Select this disk
            this.selectedDisk = diskSize;
            this.selectedPeg = pegIndex;
            this.showStatus(`Disk ${diskSize} selected! Now click on a destination peg. ✨`, 'success');
        }
        
        this.updateVisualSelection();
    }

    handlePegClick(pegIndex) {
        if (!this.gameActive) return;
        
        if (this.selectedDisk === null) {
            // Try to select top disk from this peg
            const topDisk = this.towers[pegIndex][this.towers[pegIndex].length - 1];
            if (topDisk) {
                this.handleDiskClick(topDisk, pegIndex);
            } else {
                this.showStatus('This peg is empty! Select a disk from another peg first. 📍', 'info');
            }
            return;
        }
        
        if (pegIndex === this.selectedPeg) {
            // Clicked on same peg, deselect
            this.selectedDisk = null;
            this.selectedPeg = null;
            this.showStatus('Move cancelled. Choose a disk to move! 🔄', 'info');
            this.updateVisualSelection();
            return;
        }
        
        // Try to move disk to this peg
        if (this.isValidMove(this.selectedPeg, pegIndex)) {
            this.makeMove(this.selectedPeg, pegIndex);
            this.selectedDisk = null;
            this.selectedPeg = null;
            this.updateVisualSelection();
            
            if (this.checkWinCondition()) {
                this.gameWon();
            }
        } else {
            this.showStatus('Invalid move! You cannot place a larger disk on a smaller one. ❌', 'error');
        }
    }

    isValidMove(fromPeg, toPeg) {
        if (this.towers[fromPeg].length === 0) return false;
        if (this.towers[toPeg].length === 0) return true;
        
        const diskToMove = this.towers[fromPeg][this.towers[fromPeg].length - 1];
        const topDisk = this.towers[toPeg][this.towers[toPeg].length - 1];
        
        return diskToMove < topDisk;
    }

    makeMove(fromPeg, toPeg) {
        const disk = this.towers[fromPeg].pop();
        this.towers[toPeg].push(disk);
        this.moves++;
        
        // Record the move in sequence (A, B, C, D format)
        const pegNames = ['A', 'B', 'C', 'D'];
        const moveNotation = `${pegNames[fromPeg]}->${pegNames[toPeg]}`;
        
        // Add to global manual move sequence for tracking
        if (window.app) {
            window.app.manualMoveSequence.push(moveNotation);
            if (window.app.currentPlay) {
                window.app.currentPlay.moves = [...window.app.manualMoveSequence];
                window.app.currentPlay.moveCount = this.moves;
            }
        }
        
        // Update move counter in both places
        const moveCountEl = document.getElementById('moveCount');
        const movesmadeEl = document.getElementById('movesMade');
        if (moveCountEl) moveCountEl.textContent = this.moves;
        if (movesmadeEl) movesmadeEl.textContent = this.moves;
        
        this.drawTowers();
        
        this.showStatus(`Great move! Disk ${disk} moved successfully. ✅`, 'success');
        
        // Check if game is complete after this move
        if (this.checkWinCondition()) {
            setTimeout(() => this.gameWon(), 300);
        }
    }

    updateVisualSelection() {
        // Remove all selections
        document.querySelectorAll('.disk').forEach(disk => {
            disk.classList.remove('selected');
        });
        
        document.querySelectorAll('.peg-container').forEach(peg => {
            peg.classList.remove('peg-highlight');
        });
        
        // Highlight selected disk
        if (this.selectedDisk !== null) {
            document.querySelectorAll(`.disk[data-size="${this.selectedDisk}"]`).forEach(disk => {
                if (parseInt(disk.dataset.peg) === this.selectedPeg) {
                    disk.classList.add('selected');
                }
            });
            
            // Highlight valid destination pegs
            for (let i = 0; i < this.pegCount; i++) {
                if (i !== this.selectedPeg && this.isValidMove(this.selectedPeg, i)) {
                    document.querySelector(`.peg-container[data-peg="${i}"]`).classList.add('peg-highlight');
                }
            }
        }
    }

    checkWinCondition() {
        return this.towers[this.pegCount - 1].length === this.diskCount;
    }

    async gameWon() {
        this.gameActive = false;
        const endTime = new Date();
        const duration = Math.floor((endTime - this.startTime) / 1000);
        
        // Auto-save game completion to database
        await this.autoSaveGameCompletion(duration);
        
        this.showVictoryScreen(duration);
        // Removed duplicate saveGameResult() call
    }

    showVictoryScreen(duration) {
        const victoryHTML = `
            <div class="victory-screen" id="victoryScreen">
                <div class="victory-card">
                    <h3>🏆 Congratulations!</h3>
                    <p>Well done, <strong>${this.playerName}</strong>!</p>
                    <div class="victory-stats">
                        <p>🎯 <strong>Disks:</strong> <span>${this.diskCount}</span></p>
                        <p>🔄 <strong>Moves:</strong> <span>${this.moves}</span></p>
                        <p>⏰ <strong>Time:</strong> <span>${this.formatTime(duration)}</span></p>
                        <p>🎖️ <strong>Optimal:</strong> <span>${Math.pow(2, this.diskCount) - 1} moves</span></p>
                        <p>📊 <strong>Efficiency:</strong> <span>${this.calculateEfficiency()}%</span></p>
                    </div>
                    <div class="victory-actions">
                        <button class="btn btn-primary" onclick="interactiveGame.newGame()">🆕 New Game</button>
                        <button class="btn btn-secondary" onclick="interactiveGame.closeVictoryScreen()">📋 View Leaderboard</button>
                        <button class="btn btn-success" onclick="interactiveGame.playAgain()">🔄 Play Again</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', victoryHTML);
    }

    async saveGameResult(duration) {
        try {
            const gameData = {
                player_name: this.playerName,
                disk_count: this.diskCount,
                peg_count: this.pegCount,
                moves: this.moves,
                time_taken: duration,
                is_optimal: this.moves === (Math.pow(2, this.diskCount) - 1)
            };

            console.log('Saving game result:', gameData);

            const response = await fetch('http://localhost:8000/api/leaderboard', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(gameData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Game result saved successfully!', result);
                this.showStatus('🎉 Your score has been saved to the leaderboard!', 'success');
            } else {
                const errorText = await response.text();
                console.error('Failed to save game result:', response.status, errorText);
                this.showStatus('⚠️ Score saved locally but may not appear on leaderboard.', 'warning');
            }
        } catch (error) {
            console.error('Error saving game result:', error);
            this.showStatus('⚠️ Could not connect to save score.', 'warning');
        }
    }

    calculateEfficiency() {
        const optimal = Math.pow(2, this.diskCount) - 1;
        return Math.round((optimal / this.moves) * 100);
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            if (this.startTime && this.gameActive) {
                const now = new Date();
                const elapsed = Math.floor((now - this.startTime) / 1000);
                const gameTimeEl = document.getElementById('gameTime');
                const timeElapsedEl = document.getElementById('timeElapsed');
                if (gameTimeEl) gameTimeEl.textContent = this.formatTime(elapsed);
                if (timeElapsedEl) timeElapsedEl.textContent = `${elapsed}s`;
            }
        }, 1000);
    }

    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('statusMessage');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status-message ${type}`;
        }
    }

    showHint() {
        if (!this.gameActive) return;
        
        const hints = [
            "🎯 Always move the smallest disk first in the optimal solution!",
            "📍 The smallest disk should alternate between pegs in a specific pattern.",
            "🧠 Think recursively: to move n disks, first move n-1 disks to auxiliary peg.",
            "⚡ Try to keep larger disks out of the way while moving smaller ones.",
            "🎪 The minimum number of moves is 2^n - 1, where n is the number of disks."
        ];
        
        const randomHint = hints[Math.floor(Math.random() * hints.length)];
        this.showStatus(randomHint, 'info');
    }

    resetGame() {
        if (confirm('Are you sure you want to reset the current game?')) {
            this.initializeTowers();
            this.startTime = new Date();
            this.drawTowers();
            this.showStatus('Game reset! Start moving disks. 🚀', 'info');
        }
    }

    quitGame() {
        if (confirm('Are you sure you want to quit the current game?')) {
            this.gameActive = false;
            clearInterval(this.timerInterval);
            this.setupGameUI();
            
            // Navigate back to home page
            if (window.app) {
                window.app.showSection('homeSection');
            }
        }
    }

    newGame() {
        this.closeVictoryScreen();
        this.gameActive = false;
        clearInterval(this.timerInterval);
        this.setupGameUI();
    }

    playAgain() {
        this.closeVictoryScreen();
        this.initializeTowers();
        this.gameActive = true;
        this.startTime = new Date();
        this.setupGameUI();
        this.startTimer();
        this.showStatus(`Welcome back ${this.playerName}! Let's play again! 🚀`, 'success');
    }

    closeVictoryScreen() {
        const victoryScreen = document.getElementById('victoryScreen');
        if (victoryScreen) {
            victoryScreen.remove();
        }
    }
}

// Global interactive game instance
let interactiveGame = null;

// Initialize interactive game when DOM is ready
function initializeInteractiveGame() {
    const gameContainer = document.getElementById('interactiveGameContainer');
    if (gameContainer) {
        interactiveGame = new InteractiveTowerGame(gameContainer, 3);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TowerOfHanoiApp();
    
    // Initialize interactive game if container exists
    setTimeout(initializeInteractiveGame, 100);
});

// Add notification animation styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.7;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(notificationStyles);