const API_BASE = "http://localhost:8000"; // FastAPI base URL.

// Helper to show/hide the loading overlay.
const toggleLoader = (show) => {
  const loader = document.getElementById("loader"); // Loader element.
  if (!loader) return; // Guard for pages without loader.
  loader.classList.toggle("hidden", !show); // Toggle visibility.
};

// Persist temporary data between pages.
const storage = {
  set(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value)); // Store as JSON string.
  },
  get(key, fallback = null) {
    const raw = sessionStorage.getItem(key); // Read value.
    return raw ? JSON.parse(raw) : fallback; // Parse or return fallback.
  },
  remove(key) {
    sessionStorage.removeItem(key); // Delete item.
  },
};

// Utility to build checkbox UI for cities.
const renderCityCheckboxes = (disabled = true, homeCity = null) => {
  const container = document.getElementById("city-checkboxes"); // Target container.
  if (!container) return; // Guard.
  container.innerHTML = ""; // Reset content.
  "ABCDEFGHIJ".split("").forEach((city) => {
    const wrapper = document.createElement("label"); // Label wrapper.
    wrapper.className =
      "flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-50 border border-blue-200 cursor-pointer hover:border-sky-500 transition"; // Styling.
    const checkbox = document.createElement("input"); // Checkbox input.
    checkbox.type = "checkbox"; // Set type.
    checkbox.value = city; // City label.
    checkbox.className = "accent-sky-500 h-4 w-4"; // Style checkbox.
    checkbox.disabled = disabled; // Disable until matrix is generated.
    wrapper.appendChild(checkbox); // Attach input.
    const span = document.createElement("span"); // Label text.
    span.textContent = `City ${city}`; // Display label.
    if (homeCity && city === homeCity) {
      checkbox.disabled = true; // Prevent selecting home.
      wrapper.classList.add("opacity-100", "bg-green-50"); // Dim home city.
      span.textContent = `City ${city} (HOME CITY)`; // Mark home.
      span.style.color = "green";
    }
    wrapper.appendChild(span); // Attach label.
    container.appendChild(wrapper); // Add to container.
  });
};

// Render the 10x10 distance matrix.
const renderMatrix = (matrix) => {
  const headerRow = document.getElementById("matrix-header"); // Header row.
  const body = document.getElementById("matrix-body"); // Table body.
  if (!headerRow || !body) return; // Guard.
  headerRow.innerHTML = ""; // Reset header.
  body.innerHTML = ""; // Reset body.
  const headerCells = ["", ...Array.from("ABCDEFGHIJ")]; // Header labels.
  headerCells.forEach((label) => {
    const th = document.createElement("th"); // Header cell.
    th.className = "px-2 py-1 text-sky-700 font-semibold border border-blue-200"; // Style.
    th.textContent = label; // Set text.
    headerRow.appendChild(th); // Add to header row.
  });
  matrix.forEach((row, rowIdx) => {
    const tr = document.createElement("tr"); // Row element.
    row.forEach((cell, colIdx) => {
      if (colIdx === 0) {
        const label = document.createElement("td"); // Row label.
        label.className = "font-semibold text-sky-700 border border-blue-200 bg-blue-50"; // Style.
        label.textContent = String.fromCharCode(65 + rowIdx); // A-J.
        tr.appendChild(label); // Add label cell.
      }
      const td = document.createElement("td"); // Data cell.
      td.textContent = Number(cell).toFixed(1); // Set value with one decimal.
      td.className = "text-slate-800 border border-blue-100"; // Style.
      tr.appendChild(td); // Add to row.
    });
    body.appendChild(tr); // Add row to body.
  });
};

// Build dropdowns for ordering the selected cities.
const renderOrderControls = (cities) => {
  const container = document.getElementById("order-container"); // Target container.
  if (!container) return; // Guard.
  container.innerHTML = ""; // Reset content.
  cities.forEach((city, index) => {
    const wrapper = document.createElement("div"); // Wrapper.
    wrapper.className = "space-y-2"; // Spacing.
    const label = document.createElement("label"); // Label.
    label.className = "text-sm text-slate-700 block font-medium"; // Style.
    label.textContent = `Visit #${index + 1}`; // Position label.
    const select = document.createElement("select"); // Select control.
    select.className =
      "w-full rounded-lg bg-white border border-blue-200 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none"; // Style select.
    cities.forEach((optionCity) => {
      const option = document.createElement("option"); // Option element.
      option.value = optionCity; // Value.
      option.textContent = optionCity; // Display.
      select.appendChild(option); // Add option.
    });
    select.value = city; // Default selection.
    wrapper.appendChild(label); // Add label.
    wrapper.appendChild(select); // Add select.
    container.appendChild(wrapper); // Append to container.
  });
};

// Gather selected city checkboxes.
const getSelectedCities = () => {
  const inputs = document.querySelectorAll("#city-checkboxes input[type=checkbox]"); // All checkboxes.
  return Array.from(inputs)
    .filter((box) => box.checked)
    .map((box) => box.value); // Return selected values.
};

// Initialize the home page.
const initHome = () => {
  const form = document.getElementById("player-form"); // Form element.
  if (!form) return; // Guard.
  form.addEventListener("submit", (e) => {
    e.preventDefault(); // Prevent default navigation.
    const name = document.getElementById("player-name")?.value?.trim() || ""; // Get name.
    if (name) {
      storage.set("playerName", name); // Store for later.
    } else {
      storage.remove("playerName"); // Clear if empty.
    }
    window.location.href = "game.html"; // Navigate to game page.
  });
};

// Initialize the game page.
const initGame = () => {
  renderCityCheckboxes(true); // Build checkboxes disabled until matrix generated.
  const backHome = document.getElementById("back-home"); // Back button.
  backHome?.addEventListener("click", () => (window.location.href = "index.html")); // Navigate back.

  const generateBtn = document.getElementById("generate-matrix"); // Generate button.
  const startBtn = document.getElementById("start-route"); // Start game button.
  const finishBtn = document.getElementById("finish-route"); // Finish route button.
  const statusMsg = document.getElementById("status-message"); // Status text.
  const homeLabel = document.getElementById("home-city-label"); // Home badge.

  generateBtn?.addEventListener("click", async () => {
    toggleLoader(true); // Show loader.
    statusMsg.textContent = "Generating matrix and home city..."; // Inform user.
    try {
      const res = await fetch(`${API_BASE}/generate-matrix`, { method: "POST" }); // Call API.
      if (!res.ok) throw new Error("Failed to generate matrix."); // Handle errors.
      const data = await res.json(); // Parse JSON.
      renderMatrix(data.distance_matrix); // Render matrix.
      homeLabel.textContent = data.home_city; // Show home city.
      storage.set("distanceMatrix", data.distance_matrix); // Persist matrix.
      storage.set("homeCity", data.home_city); // Persist home.
      renderCityCheckboxes(false, data.home_city); // Enable checkboxes and lock home.

      startBtn.disabled = false;                // Enable start button
      startBtn.style.backgroundColor = "rgba(25, 185, 86, 0.3)";   // Base color
      startBtn.style.cursor = "pointer";        // Pointer cursor
      startBtn.style.transition = "all 0.3s";   // Smooth transitions
      startBtn.style.boxShadow = "0 4px 6px rgba(0,0,0,0.3)"; // Shadow

      // Hover effect
      startBtn.addEventListener("mouseenter", () => {
        startBtn.style.backgroundColor = "rgba(10, 136, 58, 0.3)";
      });
      startBtn.addEventListener("mouseleave", () => {
        startBtn.style.backgroundColor = "rgba(10, 136, 58, 0.3)";
      });

      // Click effect
      startBtn.addEventListener("mousedown", () => {
        startBtn.style.transform = "scale(0.95)";
      });
      startBtn.addEventListener("mouseup", () => {
        startBtn.style.transform = "scale(1)";
      });
      
      
      statusMsg.textContent = "Matrix ready. Select cities (home is locked) and click Start Game."; // Update status.
      statusMsg.style.color = "black";
    } catch (err) {
      statusMsg.textContent = err.message; // Show error.
    } finally {
      toggleLoader(false); // Hide loader.
    }
  });

  startBtn?.addEventListener("click", () => {
    const selected = getSelectedCities().filter((c) => c !== storage.get("homeCity")); // Collect selections excluding home.
    if (!selected.length) {
      statusMsg.textContent = "Select at least one city."; // Validation message.
      statusMsg.style.color = "red";
      return; // Stop early.
    }
    renderOrderControls(selected); // Build ordering UI.

    // Scroll smoothly to "Pick Visit Order" section
    document.getElementById("order-container").scrollIntoView({ behavior: "smooth", block: "start" });

    finishBtn.disabled = false; // Enable finish.
    statusMsg.textContent = "Arrange your visit order, then calculate.";
    statusMsg.style.color = "black"; // Instruction.
  });

  finishBtn?.addEventListener("click", async () => {
    const matrix = storage.get("distanceMatrix"); // Retrieve matrix.
    const homeCity = storage.get("homeCity"); // Retrieve home.
    const selectors = document.querySelectorAll("#order-container select"); // Order selectors.
    const playerOrder = Array.from(selectors).map((s) => s.value); // Extract order.
    const uniqueCount = new Set(playerOrder).size; // Check duplicates.
    const status = document.getElementById("player-route-display"); // Display element.
    if (!matrix || !homeCity) {
      status.textContent = "Generate the matrix first."; // Validation message.
      return; // Stop early.
    }
    if (playerOrder.length === 0) {
      status.textContent = "Select cities and set their order first."; // Validation message.
      return;
    }
    if (uniqueCount !== playerOrder.length) {
      status.textContent = "Each city must appear once. home city is fixed at start/end."; // Duplicate warning.
      status.style.color = "red";
      return; // Stop early.
    }
    toggleLoader(true); // Show loader.
    try {
      const playerRes = await fetch(`${API_BASE}/calculate-player-route`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ home_city: homeCity, player_order: playerOrder, distance_matrix: matrix }),
      }); // Call player route endpoint.
      if (!playerRes.ok) throw new Error("Could not calculate player route."); // Error guard.
      const playerData = await playerRes.json(); // Parse player result.
      const solveRes = await fetch(`${API_BASE}/solve-tsp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          home_city: homeCity,
          selected_cities: playerOrder,
          distance_matrix: matrix,
        }),
      }); // Call solver endpoint.
      if (!solveRes.ok) throw new Error("Could not solve TSP."); // Error guard.
      const solveData = await solveRes.json(); // Parse solver result.
      const optimal = solveData.dynamic_programming.distance; // DP optimal distance.
      const playerScore = Math.max(10, parseInt((optimal / playerData.distance) * 100, 10)); // Score formula.
      const payload = {
        homeCity,
        distanceMatrix: matrix,
        playerRoute: playerData.route,
        playerDistance: playerData.distance,
        playerScore,
        selectedCities: playerOrder,
        algorithms: solveData,
      }; // Bundle for next page.
      storage.set("results", payload); // Persist results.
      status.textContent = `Your route: ${playerData.route.join(" → ")} (Distance: ${playerData.distance.toFixed(1)} km)`; // Show summary.
      window.location.href = "results.html"; // Navigate to results.
    } catch (err) {
      status.textContent = err.message; // Show error.
    } finally {
      toggleLoader(false); // Hide loader.
    }
  });
};

// Initialize the results page.
const initResults = () => {
  const data = storage.get("results"); // Load results.
  if (!data) {
    window.location.href = "index.html"; // Redirect if missing.
    return; // Stop.
  }
  const playerRoute = document.getElementById("player-route"); // Player route element.
  const playerDistance = document.getElementById("player-distance"); // Distance element.
  const playerScore = document.getElementById("player-score"); // Score element.
  const algorithmList = document.getElementById("algorithm-list"); // Algorithm list.
  const optimalSummary = document.getElementById("optimal-summary"); // Optimal text.
  const lossMessage = document.getElementById("loss-message"); // Loss message container.

  playerRoute.textContent = `Route: ${data.playerRoute.join(" → ")}`; // Show route.
  playerDistance.textContent = `Distance: ${data.playerDistance.toFixed(1)} km`; // Show distance.
  playerScore.textContent = `Score: ${data.playerScore}`; // Show score.
  algorithmList.innerHTML = ""; // Clear list.

  const entries = [
    ["Brute Force", data.algorithms.brute_force],
    ["Nearest Neighbor", data.algorithms.nearest_neighbor],
    ["Dynamic Programming", data.algorithms.dynamic_programming],
  ]; // Algorithm tuples.

  // Find most optimal route/distance among algorithms.
  const optimal = entries.reduce((best, [label, result]) => {
    if (result.distance < best.distance) return { label, result };
    return best;
  }, { label: "Brute Force", result: data.algorithms.brute_force });

  optimalSummary.textContent = `Best: ${optimal.label} | Distance: ${optimal.result.distance.toFixed(1)} km | Route: ${
    optimal.result.route ? optimal.result.route.join(" → ") : "N/A"
  }`; // Optimal summary.

  // Check if player lost (distance > 150% of optimal)
  const optimalDistance = optimal.result.distance;
  const playerDistanceValue = data.playerDistance;
  const lossThreshold = optimalDistance * 1.5; // 150% threshold

  if (lossMessage) {
    if (playerDistanceValue > lossThreshold) {
      lossMessage.innerHTML = `
        <div class="p-3 rounded-lg border border-red-300 bg-red-50 text-red-700">
          <strong>You lost.</strong> Your distance (${playerDistanceValue.toFixed(
            1
          )} km) was much higher than the optimal (${optimalDistance.toFixed(1)} km). Score: ${data.playerScore}
        </div>
      `;
    } else {
      lossMessage.innerHTML = "";
    }
  }

  entries.forEach(([label, result]) => {
    const li = document.createElement("li"); // List item.
    li.className = "p-3 rounded-lg bg-white border border-gray-200"; // Style.
    const routeText = result.route ? result.route.join(" → ") : "Route derived in solver"; // Route text.
    const timeMs = (result.time_seconds * 1000).toFixed(2); // Convert to ms.
    li.innerHTML = `<strong>${label}</strong>: ${routeText} | Distance: ${result.distance.toFixed(
      1
    )} km | Time: ${timeMs} ms`; // Summary.
    algorithmList.appendChild(li); // Add to list.
  });

  document.getElementById("play-again")?.addEventListener("click", () => {
    window.location.href = "game.html"; // Restart flow.
  }); // Play again handler.

  document.getElementById("play-next-round")?.addEventListener("click", () => {
    window.location.href = "game.html"; // Keep player name, start new round.
  });

  document.getElementById("play-new-game")?.addEventListener("click", () => {
    storage.remove("playerName"); // Clear stored name.
    storage.remove("results");
    storage.remove("distanceMatrix");
    storage.remove("homeCity");
    storage.remove("selectedCities");
    window.location.href = "index.html"; // Back to start.
  });
};

// Entry point to dispatch per page.
document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page; // Identify page.
  if (page === "home") initHome(); // Home page setup.
  if (page === "game") initGame(); // Game page setup.
  if (page === "results") initResults(); // Results page setup.
}); // DOM ready handler.

