
// Function to set the initial "Ready" status on page load.
function initializeUI() {
    const detailedResultsDiv = document.getElementById('detailed-results');
    if (detailedResultsDiv) {
        // The HTML element now exists, so this works safely.
        detailedResultsDiv.innerHTML = '<p style="color: #00ff00;">SYSTEM STATUS: READY. Enter pilot name and flow estimate to begin simulation.</p>';
    } else {
        console.error("Initialization Error: Cannot find element with ID 'detailed-results'.");
    }
}

// Main function triggered by the "RUN SIMULATION" button click.
async function initGraph() {
    // 1. Define the target results element
    const detailedResultsDiv = document.getElementById('detailed-results');
    
    // Safety check (should rarely fail if initializeUI ran correctly)
    if (!detailedResultsDiv) {
        console.error("Runtime Error: Cannot find element with ID 'detailed-results'.");
        return; 
    }

    // Get input values
    const playerName = document.getElementById('player-name').value;
    const maxFlowGuess = document.getElementById('max-flow-guess').value;
    const parsedMaxFlow = parseInt(maxFlowGuess);
    // 2. Client-Side Validation
    if (!playerName || !maxFlowGuess) {
        // Check for empty string
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: Please enter PILOT NAME and MAX FLOW GUESS.</p>';
        return;
    } else if (isNaN(parsedMaxFlow)) {
        // Check for non-numeric input
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: MAX FLOW GUESS must be a valid number.</p>';
        return;
    } else if (parsedMaxFlow < 1) {
        // Check for lower boundary
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: MAX FLOW GUESS must be at least 1.</p>';
        return;
    } else if (parsedMaxFlow > 50) {
        // Check for upper boundary
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: MAX FLOW GUESS exceeds the maximum limit of 50.</p>';
        return;
    }

    // Indicate that simulation is running
    detailedResultsDiv.innerHTML = '<p style="color: #ff9900;">STATUS: RUNNING SIMULATION... AWAITING BACKEND RESPONSE.</p>';

    try {
        // 3. Fetch data from the FastAPI API
        const response = await fetch('/api/traffic/new-round', { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                player_name: playerName, 
                max_flow_guess: parseInt(maxFlowGuess)
            }) 
        });
        
        // Handle server errors (400, 500, etc.)
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Server Error (${response.status}): ${errorData.detail || 'Unknown error.'}`);
        }
        
        const simulationData = await response.json(); 
        const sSideNodes = simulationData.sSideNodes || []; 
        const winStatus = simulationData.winStatus;
    
        // 4. Display the results and win/loss status
        let statusColor = (winStatus === 'Win') ? '#00ff00' : (winStatus === 'Draw') ? '#ff9900' : '#ff0000';
        detailedResultsDiv.innerHTML = `
            <p>Pilot: <strong>${simulationData.playerName}</strong> | Guess: <strong>${simulationData.playerGuess}</strong></p>
            <p>Max Flow (Edmonds-Karp): <strong>${simulationData.maxFlowEK}</strong> (${simulationData.runtimeEK_ms} ms)</p>
            <p>Max Flow (Dinic's): <strong>${simulationData.maxFlowDinic}</strong> (${simulationData.runtimeDinic_ms} ms)</p>
            <p>Game Status: <strong style="color: ${statusColor};">${winStatus}</strong>!</p>
            <p class="hint">CRITICAL FAILURE: MIN-CUT is **${simulationData.maxFlowEK}**.</p>
        `;
        
        // 5. Initialize Cytoscape.js visualization
        var cy = cytoscape({
            container: document.getElementById('cy'),
            elements: simulationData.elements,
            
            style: [
                // Node styling
                { selector: 'node', style: {
                    'label': 'data(id)',
                    'background-color': data => (data.id === 'A' ? '#28a745' : data.id === 'T' ? '#dc3545' : '#007bff'),
                    'color': '#ffffff', 'text-valign': 'center', 'text-halign': 'center', 'width': '30px', 'height': '30px',
                }},
                // Edge styling and Min-Cut Highlighting
                { selector: 'edge', style: {
                    'label': 'data(capacity)', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle',
                    'width': edge => {
                        const source = edge.data('source');
                        const target = edge.data('target');
                        return (sSideNodes.includes(source) && !sSideNodes.includes(target)) ? 4 : 2;
                    },
                    'line-color': edge => {
                        const source = edge.data('source');
                        const target = edge.data('target');
                        if (sSideNodes.includes(source) && !sSideNodes.includes(target)) {
                            return '#dc3545'; // Red for min-cut
                        }
                        return '#888'; // Grey for normal edges
                    },
                    'target-arrow-color': edge => {
                        const source = edge.data('source');
                        const target = edge.data('target');
                        if (sSideNodes.includes(source) && !sSideNodes.includes(target)) {
                            return '#dc3545'; 
                        }
                        return '#888';
                    },
                    'color': '#c7ced4', 'font-size': '10px'
                }}
            ],
            
            layout: { name: 'concentric', padding: 10 }
        });
    } catch (error) {
        console.error("Error fetching or initializing graph:", error);
        detailedResultsDiv.innerHTML = `<p style="color: red;">ERROR: CONNECTION FAILURE. ${error.message}.</p><p>Check FastAPI server status.</p>`;
    }
}

// Function to update the #leaderboard-list UL with fetched data
function updateLeaderboardUI(leaderboardData) {
    const listElement = document.getElementById('leaderboard-list');
    
    // Clear existing content
    listElement.innerHTML = ''; 

    if (leaderboardData.length === 0) {
        listElement.innerHTML = '<li>No pilot rankings available. Run a simulation to post a score!</li>';
        return;
    }

    leaderboardData.forEach((entry, index) => {
        // Format the time nicely (ensure the backend sends time in ms or a comparable unit)
        const formattedTime = `${entry.runtime_ms.toFixed(2)} ms`;
        
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            ${index + 1}. ${entry.player_name} 
            <span class="time">${formattedTime}</span>
        `;
        listElement.appendChild(listItem);
    });
}


// Function to fetch the leaderboard data from the backend API
async function fetchAndDisplayLeaderboard() {
    const listElement = document.getElementById('leaderboard-list');
    const panelTitle = document.querySelector('#leaderboard-panel .panel-title');
    
    // Set a loading state
    listElement.innerHTML = '<li>Loading rankings...</li>';
    
    // Optional: Add a temporary class for visual feedback
    panelTitle.textContent = 'GLOBAL PILOT RANKINGS // FETCHING DATA...';

    try {
        // 1. Fetch data from your FastAPI API endpoint (assuming /api/leaderboard)
        const response = await fetch('/api/traffic/leaderboard');
        
        if (!response.ok) {
            throw new Error(`Server Error (${response.status}) while fetching leaderboard.`);
        }
        
        const leaderboardData = await response.json(); 
        
        // 2. Update the UI with the fetched data
        updateLeaderboardUI(leaderboardData);

    } catch (error) {
        console.error("Error fetching leaderboard:", error);
        listElement.innerHTML = `<li style="color: red;">ERROR: Failed to load leaderboard. ${error.message}</li>`;
    } finally {
        // Restore the original title
        panelTitle.textContent = 'GLOBAL PILOT RANKINGS';
    }
}

// 6. Execute initializeUI when the document is ready.
document.addEventListener('DOMContentLoaded', initializeUI);