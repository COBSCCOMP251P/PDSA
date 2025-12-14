/**
 * TRAFFIC FLOW SIMULATOR - UNIT TESTS
 * * This script contains mock functions and test cases to verify the core
 * client-side logic of the Traffic Flow Simulator, specifically focusing on:
 * 1. Input validation in initGraph().
 * 2. Leaderboard list rendering in updateLeaderboardUI().
 * * * TO RUN: 
 * 1. In the browser console, you may need to type 'allow pasting' first.
 * 2. Paste this entire script into the console and press Enter.
 * * NOTE: This script is wrapped in an IIFE to safely mock and restore 
 * global browser functions (like document.getElementById).
 */
(async function() { // Start of the IIFE for isolation and cleanup

// --- MOCK ENVIRONMENT SETUP ---

let mockDOM = {};
let detailedResultsLog = '';
let leaderboardList = [];
let mockButtonEnabledState = true;
let mockGameStatusText = '';
let mockGameStatusClass = '';

// Store original document methods for restoration
const originalGetElementById = document.getElementById;
const originalQuerySelector = document.querySelector;
const originalCreateElement = document.createElement;

// Mock document.getElementById to return a consistent mock structure
const mockGetElementById = (id) => {
    // Mock the elements needed for validation and status updates
    switch (id) {
        case 'player-name':
            // Use trim() on the mock value itself to accurately simulate the element behavior
            return { value: mockDOM.playerName || '', trim: () => (mockDOM.playerName || '').trim() };
        case 'max-flow-guess':
            return { value: mockDOM.maxFlowGuess || '', trim: () => (mockDOM.maxFlowGuess || '').trim() };
        case 'detailed-results':
            return { 
                // Store the innerHTML set by the function
                set innerHTML(html) { detailedResultsLog = html; },
                get innerHTML() { return detailedResultsLog; }
            };
        case 'run-btn':
            return {
                set disabled(state) { mockButtonEnabledState = state; }, // State is true when disabled
                get disabled() { return mockButtonEnabledState; }
            };
        case 'game-status-input':
            return {
                set textContent(text) { mockGameStatusText = text; },
                set className(cls) { mockGameStatusClass = cls; },
                get textContent() { return mockGameStatusText; },
                get className() { return mockGameStatusClass; }
            };
        case 'leaderboard-list':
            return {
                // Simplified mock list storage
                set innerHTML(val) { leaderboardList = val === '' ? [] : [val]; },
                get innerHTML() { return leaderboardList.join(''); },
                appendChild: (node) => leaderboardList.push(node._content), // Corrected to use internal content
            };
        case 'cy':
            return {}; // Mock for visualization container
        default:
            return null;
    }
};

// Simple mock for document.createElement used in updateLeaderboardUI
const mockCreateElement = (tag) => ({ 
    tag: tag, 
    _content: '', // Internal variable to hold innerHTML content
    appendChild: (node) => { /* Mock append */ }, 
    // Getter/setter for innerHTML that uses the internal _content
    set innerHTML(val) { this._content = val; },
    get innerHTML() { return this._content; }
});

// Apply the mocks to the global document object
document.getElementById = mockGetElementById;
document.querySelector = (selector) => {
    // Mock for the panel title query in fetchAndDisplayLeaderboard
    if (selector.includes('.panel-title')) {
        return { textContent: '' };
    }
    return null;
};
document.createElement = mockCreateElement;


// Mock fetch call to immediately throw for validation tests
const mockFetch = async () => {
    throw new Error('MOCK: Network call attempted. Validation passed.');
};


// --- EXTRACTED APPLICATION LOGIC (FOR TESTING) ---

// Note: These functions are copied from the main script and rely on the mocks above.

const BASE_URL = 'http://localhost:8000'; // Define BASE_URL for completeness

/**
 * Function to update the #leaderboard-list UL with fetched data
 */
function updateLeaderboardUI(leaderboardData) {
    const listElement = document.getElementById('leaderboard-list');
    
    listElement.innerHTML = ''; 

    if (leaderboardData.length === 0) {
        listElement.innerHTML = '<li>No pilot rankings available. Run a winning simulation to post a score!</li>';
        return;
    }

    leaderboardData.forEach((entry, index) => {
        const runtime = typeof entry.runtime_ms === 'number' ? entry.runtime_ms : parseFloat(entry.runtime_ms);
        const formattedTime = `${runtime.toFixed(3)} ms`; 
        
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            ${index + 1}. ${entry.player_name} 
            <span class="time">${formattedTime}</span>
        `;
        listElement.appendChild(listItem);
    });
}

/**
 * Main function triggered by the "RUN SIMULATION" button click.
 * Note: Only the validation part is strictly tested, network is mocked.
 */
async function initGraph() {
    const detailedResultsDiv = document.getElementById('detailed-results');
    const runBtn = document.getElementById('run-btn');
    const gameStatusInput = document.getElementById('game-status-input');
    
    if (!detailedResultsDiv || !runBtn) {
        return; 
    }

    // Get and clean input values
    const playerName = document.getElementById('player-name').value.trim();
    const maxFlowGuess = document.getElementById('max-flow-guess').value.trim();
    const parsedMaxFlow = parseInt(maxFlowGuess);

    // 2. Client-Side Validation
    if (!playerName || !maxFlowGuess) {
        detailedResultsDiv.innerHTML = '<p class="error">ERROR: Please enter PILOT NAME and MAX FLOW GUESS.</p>';
        gameStatusInput.textContent = 'ERROR';
        gameStatusInput.className = 'static-input-display error';
        return;
    } else if (playerName.length > 50) { 
        detailedResultsDiv.innerHTML = '<p class="error">ERROR: PILOT NAME must be 50 characters or less.</p>';
        gameStatusInput.textContent = 'ERROR';
        gameStatusInput.className = 'static-input-display error';
        return;
    } else if (isNaN(parsedMaxFlow) || parsedMaxFlow.toString() !== maxFlowGuess) { 
        detailedResultsDiv.innerHTML = '<p class="error">ERROR: MAX FLOW GUESS must be a valid whole number.</p>';
        gameStatusInput.textContent = 'ERROR';
        gameStatusInput.className = 'static-input-display error';
        return;
    } else if (parsedMaxFlow < 5) { 
        detailedResultsDiv.innerHTML = '<p class="error">ERROR: MAX FLOW GUESS must be at least 5.</p>';
        gameStatusInput.textContent = 'ERROR';
        gameStatusInput.className = 'static-input-display error';
        return;
    } else if (parsedMaxFlow > 50) {
        detailedResultsDiv.innerHTML = '<p class="error">ERROR: MAX FLOW GUESS exceeds the maximum limit of 50.</p>';
        gameStatusInput.textContent = 'ERROR';
        gameStatusInput.className = 'static-input-display error';
        return;
    }

    // Status: Running
    detailedResultsDiv.innerHTML = '<p class="running">STATUS: RUNNING SIMULATION... AWAITING BACKEND RESPONSE.</p>';
    gameStatusInput.textContent = 'RUNNING...';
    gameStatusInput.className = 'static-input-display running';
    
    // Disable the button (CRITICAL)
    runBtn.disabled = true;

    try {
        // MOCK: This will throw the mock error, allowing us to test the finally block.
        await mockFetch(); 
    } catch (error) {
        // Simulate catching an error
        detailedResultsDiv.innerHTML = `<p class="error">ERROR: MOCK TEST FAILURE. ${error.message}.</p>`;
        gameStatusInput.textContent = 'FAILURE';
        gameStatusInput.className = 'static-input-display error';
    } finally {
        // Re-enable the button (CRITICAL UI FIX)
        runBtn.disabled = false;
    }
}


// --- TEST RUNNER UTILITY ---

let totalTests = 0;
let failedTests = 0;

/**
 * Executes a test case and reports the result.
 * This function must be async to properly await all async test functions.
 * @param {string} name - Name of the test.
 * @param {function} testFunc - Function containing the test logic.
 */
async function runTest(name, testFunc) {
    totalTests++;
    try {
        await testFunc(); // Await the function execution (whether it's sync or async)
        console.log(`[PASS] ${name}`);
    } catch (error) {
        failedTests++;
        console.error(`[FAIL] ${name}\n       Reason: ${error.message}`);
    }
}

/**
 * Asserts a condition is true.
 * @param {boolean} condition - The condition to check.
 * @param {string} message - Error message if the condition is false.
 */
function assert(condition, message) {
    if (!condition) {
        throw new Error(message || 'Assertion failed');
    }
}


// --- TEST SUITES ---

/**
 * 1. Test Client-Side Validation Logic (initGraph)
 */
async function runValidationTests() {
    console.log('\n--- 1. INIT GRAPH VALIDATION TESTS ---');

    // Helper to reset mocks before each test
    const resetMocks = () => {
        mockDOM = {};
        detailedResultsLog = '';
        mockButtonEnabledState = false; // Button starts enabled (not disabled)
        mockGameStatusText = '';
        mockGameStatusClass = '';
    };

    // Test Case 1: Missing Player Name
    await runTest('Missing Player Name', async () => {
        resetMocks();
        mockDOM.maxFlowGuess = '10';
        await initGraph();
        assert(detailedResultsLog.includes('ERROR: Please enter PILOT NAME and MAX FLOW GUESS'), 'Did not catch missing name');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });

    // Test Case 2: Missing Max Flow Guess
    await runTest('Missing Max Flow Guess', async () => {
        resetMocks();
        mockDOM.playerName = 'TestPilot';
        await initGraph();
        assert(detailedResultsLog.includes('ERROR: Please enter PILOT NAME and MAX FLOW GUESS'), 'Did not catch missing guess');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });

    // Test Case 3: Max Flow Guess too low (4)
    await runTest('Max Flow Guess too low (4)', async () => {
        resetMocks();
        mockDOM.playerName = 'TestPilot';
        mockDOM.maxFlowGuess = '4';
        await initGraph();
        assert(detailedResultsLog.includes('MAX FLOW GUESS must be at least 5'), 'Did not catch low guess');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });
    
    // Test Case 4: Max Flow Guess too high (51)
    await runTest('Max Flow Guess too high (51)', async () => {
        resetMocks();
        mockDOM.playerName = 'TestPilot';
        mockDOM.maxFlowGuess = '51';
        await initGraph();
        assert(detailedResultsLog.includes('MAX FLOW GUESS exceeds the maximum limit of 50'), 'Did not catch high guess');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });

    // Test Case 5: Non-integer input (Float)
    await runTest('Non-integer input (Float)', async () => {
        resetMocks();
        mockDOM.playerName = 'TestPilot';
        mockDOM.maxFlowGuess = '12.5';
        await initGraph();
        assert(detailedResultsLog.includes('MAX FLOW GUESS must be a valid whole number'), 'Did not reject float input');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });

    // Test Case 6: Non-numeric input (Text)
    await runTest('Non-numeric input (Text)', async () => {
        resetMocks();
        mockDOM.playerName = 'TestPilot';
        mockDOM.maxFlowGuess = 'Twelve';
        await initGraph();
        assert(detailedResultsLog.includes('MAX FLOW GUESS must be a valid whole number'), 'Did not reject text input');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });
    
    // Test Case 7: Finally block re-enables button after mock failure
    await runTest('Finally block re-enables button after mock failure', async () => {
        resetMocks();
        mockDOM.playerName = 'TestPilot';
        mockDOM.maxFlowGuess = '15'; // Valid input to pass validation
        await initGraph();
        // After mock failure and finally block, the button must be re-enabled (state=false)
        assert(mockButtonEnabledState === false, 'Button must be re-enabled by finally block (state should be false/enabled)');
        assert(detailedResultsLog.includes('MOCK TEST FAILURE'), 'Error message should reflect the failure');
    });
    
    // Test Case 8: Inputs with Leading/Trailing Whitespace (Testing .trim())
    await runTest('Valid input with whitespace (trimming check)', async () => {
        resetMocks();
        mockDOM.playerName = '   TrimmedPilot   ';
        mockDOM.maxFlowGuess = ' 15 ';
        await initGraph();
        // Since input is valid, it should proceed to disable the button and attempt mock fetch (which fails)
        assert(mockButtonEnabledState === false, 'Button must be re-enabled after processing valid, trimmed input (state should be false/enabled)');
        assert(detailedResultsLog.includes('MOCK TEST FAILURE'), 'Should proceed past validation and hit mock failure');
    });

    // Test Case 9: Player Name exceeds 50 characters
    await runTest('Player Name too long (> 50)', async () => {
        resetMocks();
        mockDOM.playerName = 'A'.repeat(51);
        mockDOM.maxFlowGuess = '10';
        await initGraph();
        assert(detailedResultsLog.includes('PILOT NAME must be 50 characters or less'), 'Did not catch long player name');
        assert(mockButtonEnabledState === false, 'Button should not be disabled after validation fail');
    });
}

/**
 * 2. Test Leaderboard UI Update Logic
 */
async function runLeaderboardTests() {
    console.log('\n--- 2. LEADERBOARD UI TESTS ---');
    leaderboardList = []; // Reset leaderboard mock

    // Test Case 1: Empty Leaderboard
    await runTest('Update UI with Empty Leaderboard', () => {
        leaderboardList = [];
        updateLeaderboardUI([]);
        const result = leaderboardList.join('');
        assert(result.includes('No pilot rankings available. Run a winning simulation to post a score!'), 'Did not display empty message');
        assert(leaderboardList.length === 1, 'Should contain only one list item (the message)');
    });
    
    // Test Case 2: Populated Leaderboard
    await runTest('Update UI with Populated Leaderboard', () => {
        leaderboardList = []; // Reset list
        const mockData = [
            { player_name: 'Alpha', runtime_ms: 10.12345 },
            { player_name: 'Beta', runtime_ms: 500.5 },
        ];
        updateLeaderboardUI(mockData);
        
        const result = leaderboardList.join(' ');
        
        // Check for player name and index
        assert(result.includes('1. Alpha'), 'Missing first entry');
        assert(result.includes('2. Beta'), 'Missing second entry');
        
        // Check for formatted time
        assert(result.includes('10.123 ms'), 'Runtime was not formatted to 3 decimal places');
        
        assert(leaderboardList.length === 2, 'Should contain exactly two list items');
    });
}


// --- EXECUTION ---

async function runAllTests() {
    console.log('--- STARTING UNIT TESTS ---');
    // Await all test suites
    await runValidationTests();
    await runLeaderboardTests();
    console.log('\n--- TEST SUMMARY ---');
    if (failedTests === 0) {
        console.log(`✅ All ${totalTests} tests passed successfully.`);
    } else {
        console.error(`❌ ${failedTests} of ${totalTests} tests failed.`);
    }
    
    // --- CLEANUP ---
    // Restore original document functions after running tests
    document.getElementById = originalGetElementById;
    document.querySelector = originalQuerySelector;
    document.createElement = originalCreateElement;
    console.log('Mocks restored.');
}

await runAllTests();

})(); 