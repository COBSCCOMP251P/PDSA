import { initHome } from './home.js';
import { initGame } from './game.js';
import { initResults } from './results.js';

document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    if (page === "home") initHome();
    if (page === "game") initGame();
    if (page === "results") initResults();
});
