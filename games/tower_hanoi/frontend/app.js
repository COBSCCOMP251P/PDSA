/**
 * Tower of Hanoi Interactive Game - Frontend Application
 * Manages UI interactions, API calls, and game visualization
 */

class TowerOfHanoiApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/hanoi';
        this.currentRound = null;
        this.algorithmChart = null;
        this.statsChart = null;
        
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
        document.getElementById('gameBtn').addEventListener('click', () => this.showSection('gameSection'));
        document.getElementById('leaderboardBtn').addEventListener('click', () => {
            this.showSection('leaderboardSection');
            this.loadLeaderboard();
        });
        document.getElementById('algorithmsBtn').addEventListener('click', () => {
            this.showSection('algorithmsSection');
            this.loadAlgorithmStats();
        });
        document.getElementById('aboutBtn').addEventListener('click', () => this.showSection('aboutSection'));

        // Hero buttons
        document.getElementById('startGameBtn').addEventListener('click', () => this.showSection('gameSection'));
        document.getElementById('viewLeaderboardBtn').addEventListener('click', () => {
            this.showSection('leaderboardSection');
            this.loadLeaderboard();
        });

        // Game controls
        document.getElementById('createRoundBtn').addEventListener('click', () => this.createRound());
        
        // Disk count preview
        document.getElementById('diskCountSelect').addEventListener('change', () => this.updateDiskPreview());
        document.getElementById('pegCount').addEventListener('change', () => this.updateDiskPreview());

        // Refresh buttons
        document.getElementById('refreshLeaderboardBtn').addEventListener('click', () => this.loadLeaderboard());
        document.getElementById('refreshStatsBtn').addEventListener('click', () => this.loadAlgorithmStats());
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
            'gameSection': 'gameBtn',
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
            
            // Backend expects n_disks and peg_count
            const requestData = {
                peg_count: pegCount,
                n_disks: diskCountSelect ? parseInt(diskCountSelect) : 3  // Default to 3 if not selected
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
                    window.interactiveGame = new InteractiveTowerGame(gameContainer, roundData.n_disks);
                    console.log('Interactive game initialized with', roundData.n_disks, 'disks');
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
            const leaderboard = await this.apiCall('/leaderboard?limit=20');
            this.displayLeaderboard(leaderboard);
        } catch (error) {
            console.error('Error loading leaderboard:', error);
        }
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
                    <th>Best Moves</th>
                    <th>Avg Moves</th>
                    <th>Correct Solutions</th>
                    <th>Total Submissions</th>
                    <th>Last Submission</th>
                </tr>
            </thead>
            <tbody>
                ${leaderboard.map((player, index) => `
                    <tr>
                        <td class="rank">#${index + 1}</td>
                        <td>${player.name}</td>
                        <td>${player.best_moves || '-'}</td>
                        <td>${player.avg_moves ? player.avg_moves.toFixed(1) : '-'}</td>
                        <td>${player.correct_submissions}</td>
                        <td>${player.total_submissions}</td>
                        <td>${player.last_submission ? new Date(player.last_submission).toLocaleDateString() : '-'}</td>
                    </tr>
                `).join('')}
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
            // Show preview with random disk count (7 as example)
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
}

/**
 * Interactive Tower of Hanoi Game Class
 * Handles visual gameplay with click-to-move functionality
 */
class InteractiveTowerGame {
    constructor(container, diskCount = 3) {
        if (!container) {
            throw new Error('Container element is required for InteractiveTowerGame');
        }
        
        this.container = container;
        this.diskCount = diskCount;
        this.towers = [[], [], []];
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
        this.towers = [[], [], []];
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
            <div class="player-setup ${this.gameActive ? 'hidden' : ''}">
                <div class="setup-card">
                    <h4>🎮 Start New Game</h4>
                    <div class="input-group">
                        <input type="text" id="playerNameInput" placeholder="Enter your name" maxlength="50" required>
                        <select id="gameDiskCount">
                            <option value="3" ${this.diskCount === 3 ? 'selected' : ''}>3 Disks</option>
                            <option value="4" ${this.diskCount === 4 ? 'selected' : ''}>4 Disks</option>
                            <option value="5" ${this.diskCount === 5 ? 'selected' : ''}>5 Disks</option>
                            <option value="6" ${this.diskCount === 6 ? 'selected' : ''}>6 Disks</option>
                            <option value="7" ${this.diskCount === 7 ? 'selected' : ''}>7 Disks</option>
                        </select>
                        <button class="btn btn-primary" onclick="interactiveGame.startGame()">Start Game</button>
                    </div>
                </div>
            </div>

            <div class="player-info ${this.gameActive ? '' : 'hidden'}">
                <div class="player-card">
                    <div class="player-name">
                        <span>🎯</span>
                        <span id="currentPlayerName">${this.playerName}</span>
                    </div>
                    <div class="game-stats">
                        <div class="stat">
                            <span class="stat-label">Moves</span>
                            <span class="stat-value" id="moveCount">${this.moves}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Time</span>
                            <span class="stat-value" id="gameTime">00:00</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Disks</span>
                            <span class="stat-value">${this.diskCount}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="game-status">
                <div id="statusMessage" class="status-message info">
                    Click on the top disk of any peg to select it, then click on a destination peg to move it.
                </div>
            </div>

            <div class="pegs-container" id="pegsContainer">
                <!-- Towers will be drawn here -->
            </div>

            <div class="game-controls ${this.gameActive ? '' : 'hidden'}">
                <button class="btn btn-secondary" onclick="interactiveGame.resetGame()">🔄 Reset</button>
                <button class="btn btn-warning" onclick="interactiveGame.showHint()">💡 Hint</button>
                <button class="btn btn-danger" onclick="interactiveGame.quitGame()">🚪 Quit</button>
            </div>
        `;
        
        this.drawTowers();
    }

    startGame() {
        const nameInput = document.getElementById('playerNameInput');
        const diskSelect = document.getElementById('gameDiskCount');
        
        if (!nameInput.value.trim()) {
            this.showStatus('Please enter your name!', 'error');
            return;
        }

        this.playerName = nameInput.value.trim();
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
        const pegWidth = Math.floor(canvasWidth / 3) - 10;
        
        for (let i = 0; i < 3; i++) {
            const pegContainer = document.createElement('div');
            pegContainer.className = 'peg-container';
            pegContainer.dataset.peg = i;
            pegContainer.style.cssText = `
                width: ${pegWidth}px;
                height: ${canvasHeight}px;
                display: flex;
                flex-direction: column-reverse;
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
            
            // Add peg label
            const pegLabel = document.createElement('div');
            pegLabel.style.cssText = `
                position: absolute;
                top: 5px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(59, 130, 246, 0.8);
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                z-index: 2;
            `;
            pegLabel.textContent = ['Source', 'Auxiliary', 'Target'][i];
            pegContainer.appendChild(pegLabel);
            
            // Add disks
            const disks = this.towers[i];
            for (let j = 0; j < disks.length; j++) {
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
                
                // Mark top disk as movable
                if (j === disks.length - 1) {
                    diskElement.classList.add('movable');
                }
                
                pegContainer.appendChild(diskElement);
            }
            
            pegsContainer.appendChild(pegContainer);
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
        
        document.getElementById('moveCount').textContent = this.moves;
        this.drawTowers();
        
        this.showStatus(`Great move! Disk ${disk} moved successfully. ✅`, 'success');
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
            for (let i = 0; i < 3; i++) {
                if (i !== this.selectedPeg && this.isValidMove(this.selectedPeg, i)) {
                    document.querySelector(`.peg-container[data-peg="${i}"]`).classList.add('peg-highlight');
                }
            }
        }
    }

    checkWinCondition() {
        return this.towers[2].length === this.diskCount;
    }

    gameWon() {
        this.gameActive = false;
        const endTime = new Date();
        const duration = Math.floor((endTime - this.startTime) / 1000);
        
        this.showVictoryScreen(duration);
        this.saveGameResult(duration);
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
                moves: this.moves,
                time_taken: duration,
                is_optimal: this.moves === (Math.pow(2, this.diskCount) - 1)
            };

            console.log('Saving game result:', gameData);

            const response = await fetch('/api/hanoi/save-game', {
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
                document.getElementById('gameTime').textContent = this.formatTime(elapsed);
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
    new TowerOfHanoiApp();
    
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