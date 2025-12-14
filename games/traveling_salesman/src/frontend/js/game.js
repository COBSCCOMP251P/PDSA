import { renderCityCheckboxes, toggleLoader, storage, renderMatrix, getSelectedCities, renderOrderControls } from "./utils.js";
import { generateMatrix, calculatePlayerRoute, solveTSP, saveResult } from "./api.js";

export const initGame = () => {
    renderCityCheckboxes(true);
    const backHome = document.getElementById("back-home");
    backHome?.addEventListener("click", () => (window.location.href = "index.html"));

    const generateBtn = document.getElementById("generate-matrix");
    const startBtn = document.getElementById("start-route");
    const finishBtn = document.getElementById("finish-route");
    const statusMsg = document.getElementById("status-message");
    const homeLabel = document.getElementById("home-city-label");

    generateBtn?.addEventListener("click", async () => {
        toggleLoader(true);
        statusMsg.textContent = "Generating matrix and home city...";
        try {
            const data = await generateMatrix();
            renderMatrix(data.distance_matrix);
            homeLabel.textContent = data.home_city;
            storage.set("distanceMatrix", data.distance_matrix);
            storage.set("homeCity", data.home_city);
            renderCityCheckboxes(false, data.home_city);

            startBtn.disabled = false;
            startBtn.style.backgroundColor = "rgba(25, 185, 86, 0.3)";
            startBtn.style.cursor = "pointer";
            startBtn.style.transition = "all 0.3s";
            startBtn.style.boxShadow = "0 4px 6px rgba(0,0,0,0.3)";

            startBtn.addEventListener("mouseenter", () => { startBtn.style.backgroundColor = "rgba(10, 136, 58, 0.3)"; });
            startBtn.addEventListener("mouseleave", () => { startBtn.style.backgroundColor = "rgba(10, 136, 58, 0.3)"; });
            startBtn.addEventListener("mousedown", () => { startBtn.style.transform = "scale(0.95)"; });
            startBtn.addEventListener("mouseup", () => { startBtn.style.transform = "scale(1)"; });

            statusMsg.textContent = "Matrix ready. Select cities (home is locked) and click Start Game.";
            statusMsg.style.color = "black";
        } catch (err) {
            statusMsg.textContent = err.message;
        } finally {
            toggleLoader(false);
        }
    });

    startBtn?.addEventListener("click", () => {
        const selected = getSelectedCities().filter((c) => c !== storage.get("homeCity"));
        if (!selected.length) {
            statusMsg.textContent = "Select at least one city.";
            statusMsg.style.color = "red";
            return;
        }
        renderOrderControls(selected);
        document.getElementById("order-container").scrollIntoView({ behavior: "smooth", block: "start" });
        finishBtn.disabled = false;
        statusMsg.textContent = "Arrange your visit order, then calculate.";
        statusMsg.style.color = "black";
    });

    finishBtn?.addEventListener("click", async () => {
        const matrix = storage.get("distanceMatrix");
        const homeCity = storage.get("homeCity");
        const selectors = document.querySelectorAll("#order-container select");
        const playerOrder = Array.from(selectors).map((s) => s.value);
        const uniqueCount = new Set(playerOrder).size;
        const status = document.getElementById("player-route-display");

        if (!matrix || !homeCity) {
            status.textContent = "Generate the matrix first.";
            return;
        }
        if (playerOrder.length === 0) {
            status.textContent = "Select cities and set their order first.";
            return;
        }
        if (uniqueCount !== playerOrder.length) {
            status.textContent = "Each city must appear once. home city is fixed at start/end.";
            status.style.color = "red";
            return;
        }

        toggleLoader(true);
        try {
            const playerData = await calculatePlayerRoute({ home_city: homeCity, player_order: playerOrder, distance_matrix: matrix });
            const solveData = await solveTSP({ home_city: homeCity, selected_cities: playerOrder, distance_matrix: matrix });

            const optimal = solveData.dynamic_programming.distance;
            const playerScore = Math.max(10, parseInt((optimal / playerData.distance) * 100, 10));
            const payload = {
                homeCity,
                distanceMatrix: matrix,
                playerRoute: playerData.route,
                playerDistance: playerData.distance,
                playerScore,
                selectedCities: playerOrder,
                algorithms: solveData,
            };
            storage.set("results", payload);
            
            // Save to database
            try {
                const playerName = storage.get("playerName") || "Anonymous";
                console.log("Attempting to save result to database...", playerName);
                const saveResponse = await saveResult({
                    player_name: playerName,
                    home_city: homeCity,
                    selected_cities: playerOrder,
                    brute_force_distance: solveData.brute_force.distance,
                    nearest_neighbor_distance: solveData.nearest_neighbor.distance,
                    dp_distance: solveData.dynamic_programming.distance,
                    player_distance: playerData.distance,
                    score: playerScore,
                    algorithm_times: {
                        brute_force_time: solveData.brute_force.time_seconds,
                        nearest_neighbor_time: solveData.nearest_neighbor.time_seconds,
                        dp_time: solveData.dynamic_programming.time_seconds
                    }
                });
                console.log("✅ Result saved to database successfully:", saveResponse);
            } catch (saveErr) {
                console.error("❌ Failed to save to database:", saveErr);
                // Continue to results page even if save fails
            }
            
            status.textContent = `Your route: ${playerData.route.join(" → ")} (Distance: ${playerData.distance.toFixed(1)} km)`;
            window.location.href = "results.html";
        } catch (err) {
            status.textContent = err.message;
        } finally {
            toggleLoader(false);
        }
    });
};
