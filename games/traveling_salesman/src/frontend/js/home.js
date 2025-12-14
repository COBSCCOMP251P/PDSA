import { storage } from "./utils.js";

export const initHome = () => {
    const form = document.getElementById("player-form");
    if (!form) return;
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const name = document.getElementById("player-name")?.value?.trim() || "";
        if (name) {
            storage.set("playerName", name);
        } else {
            storage.remove("playerName");
        }
        window.location.href = "game.html";
    });
};
