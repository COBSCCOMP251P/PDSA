// Global variable to store the graph data elements for the subsequent simulation run
let currentGraphElements = null;

// Function to set the initial "Ready" status on page load.
function initializeUI() {
    const detailedResultsDiv = document.getElementById('detailed-results');
    if (detailedResultsDiv) {
        // Updated initial message to reflect the new workflow
        detailedResultsDiv.innerHTML = '<p style="color: #00ff00;">SYSTEM STATUS: READY. Click **GENERATE NEW GRAPH** to start a new round.</p>';
    } else {
        console.error("Initialization Error: Cannot find element with ID 'detailed-results'.");
    }
}

// Function to initialize Cytoscape.js
function renderGraph(elements, sSideNodes = []) {
    // Clear the previous graph visualization
    document.getElementById('cy').innerHTML = ''; 
    
    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: elements,
        
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
                    // Only highlight if min-cut results are available (sSideNodes is populated)
                    return (sSideNodes.length > 0 && sSideNodes.includes(source) && !sSideNodes.includes(target)) ? 4 : 2;
                },
                'line-color': edge => {
                    const source = edge.data('source');
                    const target = edge.data('target');
                    if (sSideNodes.length > 0 && sSideNodes.includes(source) && !sSideNodes.includes(target)) {
                        return '#dc3545'; // Red for min-cut
                    }
                    return '#888'; // Grey for normal edges
                },
                'target-arrow-color': edge => {
                    const source = edge.data('source');
                    const target = edge.data('target');
                    if (sSideNodes.length > 0 && sSideNodes.includes(source) && !sSideNodes.includes(target)) {
                        return '#dc3545'; 
                    }
                    return '#888';
                },
                'color': '#c7ced4', 'font-size': '10px'
            }}
        ],
        
        layout: { name: 'concentric', padding: 10 }
    });
}

/**
 * NEW FUNCTION: Fetches and displays a new random graph from the backend.
 * Stores the graph elements in a global variable for the simulation run.
 */
async function generateAndDisplayGraph() {
    const detailedResultsDiv = document.getElementById('detailed-results');
    if (!detailedResultsDiv) {
        console.error("Initialization Error: Cannot find element with ID 'detailed-results'.");
        return; 
    }
    
    detailedResultsDiv.innerHTML = '<p style="color: #ff9900;">STATUS: GENERATING GRAPH... AWAITING BACKEND RESPONSE.</p>';
    currentGraphElements = null; // Clear previous graph data
    
    try {
        // Calls the new GET endpoint
        const response = await fetch('/api/traffic/generate-graph', { method: 'GET' });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Server Error (${response.status}): ${errorData.detail || 'Unknown error.'}`);
        }
        
        const graphData = await response.json(); 
        
        // Store the graph data globally for the next simulation run
        currentGraphElements = graphData.elements;
        
        // Render the graph with no min-cut highlight yet
        renderGraph(currentGraphElements);
        
        detailedResultsDiv.innerHTML = '<p style="color: #00ff00;">STATUS: GRAPH GENERATED. Enter pilot name and flow estimate to run simulation.</p>';

    } catch (error) {
        console.error("Error fetching or initializing graph:", error);
        detailedResultsDiv.innerHTML = `<p style="color: red;">ERROR: GRAPH GENERATION FAILURE. ${error.message}.</p><p>Check FastAPI server status.</p>`;
    }
}


/**
 * Main function triggered by the "RUN SIMULATION" button click.
 * Now uses the globally stored graph data.
 */
async function initGraph() {
    // 1. Define the target results element
    const detailedResultsDiv = document.getElementById('detailed-results');
    
    // Safety check for graph existence
    if (!currentGraphElements) {
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: Please **GENERATE GRAPH** first!</p>';
        return;
    }

    // Get input values
    const playerName = document.getElementById('player-name').value;
    const maxFlowGuess = document.getElementById('max-flow-guess').value;
    const parsedMaxFlow = parseInt(maxFlowGuess);
    const gameStatusInput = document.getElementById('game-status-input'); 

    // 2. Client-Side Validation
    if (!playerName || !maxFlowGuess) {
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: Please enter PILOT NAME and MAX FLOW GUESS.</p>';
        return;
    } else if (playerName.length > 50) { 
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: PILOT NAME must be 50 characters or less.</p>';
        return;
    } else if (isNaN(parsedMaxFlow)) {
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: MAX FLOW GUESS must be a valid number.</p>';
        return;
    } else if (parsedMaxFlow < 5) { 
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: MAX FLOW GUESS must be at least 5.</p>';
        return;
    } else if (parsedMaxFlow > 50) {
        detailedResultsDiv.innerHTML = '<p style="color: red;">ERROR: MAX FLOW GUESS exceeds the maximum limit of 50.</p>';
        return;
    }

    // Indicate that simulation is running
    detailedResultsDiv.innerHTML = '<p style="color: #ff9900;">STATUS: RUNNING SIMULATION... AWAITING BACKEND RESPONSE.</p>';
    gameStatusInput.textContent = 'RUNNING...'; 
    gameStatusInput.style.color = '#ff9900';

    try {
        // 3. Fetch data from the FastAPI API (Now POSTs the graph elements along with guess)
        const response = await fetch('/api/traffic/run-simulation', { // *** NEW ENDPOINT NAME
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                player_name: playerName, 
                max_flow_guess: parseInt(maxFlowGuess),
                graph_elements: currentGraphElements // *** PASS THE GRAPH DATA
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

        if (simulationData.maxFlowEK !== simulationData.maxFlowDinic) {
            detailedResultsDiv.innerHTML += '<p style="color: orange; font-weight: bold;">WARNING: Algorithm inconsistency detected (EK != Dinic). Backend used the faster result.</p>';
        }
    
        // 4. Display the results and win/loss status
        let statusColor = (winStatus === 'Win') ? '#00ff00' : (winStatus === 'Draw') ? '#ff9900' : '#ff0000';
        detailedResultsDiv.innerHTML = `
            <p>Pilot: <strong>${simulationData.playerName}</strong> | Guess: <strong>${simulationData.playerGuess}</strong></p>
            <p>Max Flow (Edmonds-Karp): <strong>${simulationData.maxFlowEK}</strong> (${simulationData.runtimeEK_ms} ms)</p>
            <p>Max Flow (Dinic's): <strong>${simulationData.maxFlowDinic}</strong> (${simulationData.runtimeDinic_ms} ms)</p>
            <p>Game Status: <strong style="color: ${statusColor};">${winStatus}</strong>!</p>
            <p class="hint">CRITICAL FAILURE: MIN-CUT is **${simulationData.maxFlowEK}**.</p>
        `;

        // Post-run status update:
        gameStatusInput.textContent = winStatus.toUpperCase(); 
        gameStatusInput.style.color = statusColor; 
        
        // 5. Initialize Cytoscape.js visualization with Min-Cut highlight
        renderGraph(currentGraphElements, sSideNodes);

        // Clear the global graph data to force a new generation next round
        currentGraphElements = null;

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
        // Format the time nicely
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
    
    //Add a temporary class for visual feedback
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