import { storage } from "./utils.js";
import { saveResult } from "./api.js";

export const initResults = async () => {
    const data = storage.get("results");
    if (!data) {
        window.location.href = "index.html";
        return;
    }

    const playerRoute = document.getElementById("player-route");
    const playerDistance = document.getElementById("player-distance");
    const playerScore = document.getElementById("player-score");
    const algorithmList = document.getElementById("algorithm-list");
    const optimalSummary = document.getElementById("optimal-summary");
    const fastestSummary = document.getElementById("fastest-summary");
    const lossMessage = document.getElementById("loss-message");

    playerRoute.textContent = `Route: ${data.playerRoute.join(" → ")}`;
    playerDistance.textContent = `Distance: ${data.playerDistance.toFixed(1)} km`;
    playerScore.textContent = `Score: ${data.playerScore}`;
    algorithmList.innerHTML = "";

    const entries = [
        ["Brute Force", data.algorithms.brute_force],
        ["Nearest Neighbor", data.algorithms.nearest_neighbor],
        ["Dynamic Programming", data.algorithms.dynamic_programming],
    ];

    // Optimal distance
    const optimal = entries.reduce((best, [label, result]) => {
        if (result.distance < best.result.distance) return { label, result };
        return best;
    }, { label: "Brute Force", result: data.algorithms.brute_force });

    if (optimalSummary)
        optimalSummary.textContent = `Best: ${optimal.label} | Distance: ${optimal.result.distance.toFixed(1)} km | Route: ${optimal.result.route ? optimal.result.route.join(" → ") : "N/A"
            }`;

    // Fastest algorithm
    const fastest = entries.reduce((best, [label, result]) => {
        if (result.time_seconds < best.result.time_seconds) return { label, result };
        return best;
    }, { label: "Brute Force", result: data.algorithms.brute_force });

    if (fastestSummary)
        fastestSummary.textContent = `Fastest Algorithm: ${fastest.label} | Distance: ${fastest.result.distance.toFixed(1)} km | Time: ${(fastest.result.time_seconds * 1000).toFixed(2)} ms`;

    // Save result to database
    const playerName = storage.get("playerName") || "Anonymous";
    console.log("🎮 Saving result for player:", playerName);
    console.log("🎮 Data to save:", {
        home_city: data.homeCity,
        selected_cities: data.selectedCities,
        player_distance: data.playerDistance,
        score: data.playerScore
    });
    
    try {
        const savePayload = {
            player_name: playerName,
            home_city: data.homeCity,
            selected_cities: data.selectedCities,
            brute_force_distance: data.algorithms.brute_force.distance,
            nearest_neighbor_distance: data.algorithms.nearest_neighbor.distance,
            dp_distance: data.algorithms.dynamic_programming.distance,
            player_distance: data.playerDistance,
            score: data.playerScore,
            algorithm_times: {
                brute_force_time: data.algorithms.brute_force.time_seconds,
                nearest_neighbor_time: data.algorithms.nearest_neighbor.time_seconds,
                dp_time: data.algorithms.dynamic_programming.time_seconds
            }
        };
        console.log("🎮 Full payload:", JSON.stringify(savePayload));
        const result = await saveResult(savePayload);
        console.log("✅ Result saved to database:", result);
    } catch (err) {
        console.error("❌ Failed to save result:", err);
    }

    const optimalDistance = optimal.result.distance;
    const playerDistanceValue = data.playerDistance;
    const lossThreshold = optimalDistance * 1.5;

    if (lossMessage) {
        if (playerDistanceValue > lossThreshold) {
            lossMessage.innerHTML = `
        <div class="p-3 rounded-lg border border-red-300 bg-red-50 text-red-700">
          <strong>You lost.</strong> Your distance (${playerDistanceValue.toFixed(1)} km) was much higher than the optimal (${optimalDistance.toFixed(1)} km). Score: ${data.playerScore}
        </div>
      `;
        } else {
            lossMessage.innerHTML = "";
        }
    }

    entries.forEach(([label, result]) => {
        const li = document.createElement("li");
        li.className = "p-3 rounded-lg bg-white border border-gray-200";
        const routeText = result.route ? result.route.join(" → ") : "Route derived in solver";
        const timeMs = (result.time_seconds * 1000).toFixed(2);
        li.innerHTML = `<strong>${label}</strong>: ${routeText} | Distance: ${result.distance.toFixed(1)} km | Time: ${timeMs} ms`;
        algorithmList.appendChild(li);
    });

    document.getElementById("play-again")?.addEventListener("click", () => { window.location.href = "game.html"; });
    document.getElementById("play-next-round")?.addEventListener("click", () => { window.location.href = "game.html"; });
    document.getElementById("play-new-game")?.addEventListener("click", () => {
        storage.remove("playerName");
        storage.remove("results");
        storage.remove("distanceMatrix");
        storage.remove("homeCity");
        storage.remove("selectedCities");
        window.location.href = "index.html";
    });
};
