# Traveling Salesman Frontend

Static, framework-free UI built with HTML, vanilla JS, and Tailwind via CDN.

## Pages
- `index.html` — welcome screen, optional player name, start button.
- `game.html` — city selection, matrix generation, route ordering, distance calculation.
- `results.html` — shows player vs algorithms and save-to-DB action.

## How to Use
1. Open `index.html` in your browser (or serve `frontend/` statically).
2. On `game.html`, click **Generate Distances** to get a random matrix and home city.
3. Pick cities (A–J), arrange the visit order, then click **Calculate & View Results**.
4. On `results.html`, review scores and press **Save Result To Database** to persist.

## Notes
- Requires backend running at `http://localhost:8000` (adjust `API_BASE` in `script.js` if needed).
- Responsive layout uses Tailwind utility classes; a small spinner is defined in `styles.css`.
- All logic lives in `script.js`; data is passed between pages via `sessionStorage`.
