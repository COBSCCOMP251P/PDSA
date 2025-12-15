import { API_BASE } from "./config.js";

export const generateMatrix = async () => {
    const res = await fetch(`${API_BASE}/generate-matrix`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to generate matrix.");
    return res.json();
};

export const calculatePlayerRoute = async (payload) => {
    const res = await fetch(`${API_BASE}/calculate-player-route`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Could not calculate player route.");
    return res.json();
};

export const solveTSP = async (payload) => {
    const res = await fetch(`${API_BASE}/solve-tsp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Could not solve TSP.");
    return res.json();
};

export const saveResult = async (payload) => {
    const res = await fetch(`${API_BASE}/save-result`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!res.ok) {
        console.error("Failed to save result to database");
        return { message: "Failed to save" };
    }
    return res.json();
};
