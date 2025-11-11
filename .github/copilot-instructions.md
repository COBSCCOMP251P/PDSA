<!--
Guidance for AI coding agents working on the PDSA repository.
Generated: summarize only repository-discoverable facts and concrete next steps.
-->
# Copilot instructions — PDSA

Quick context
- Repository purpose (from `README.md`): "Interactive algorithm based game collection built with HTML, CSS, JS, Python and MySQL for PDSA coursework."
- Current repo root (time of writing): `README.md`, `LICENSE`, and a `.specstory/` folder. No application source files were detected in the repository root.

How to get productive
- Start by opening `README.md` (root) and `.specstory/.what-is-this.md` to understand any local conventions or backups. Example: `.specstory/.what-is-this.md` mentions backups of `.github/copilot-instructions.md` and derived cursor rules.
- Run a quick workspace search for common manifest/build files: `package.json`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `Dockerfile`, `Makefile`, `index.html`, `app.py`, `main.py`. If none are present, ask the repository owner where the source lives or which branch contains the application code.

What to expect in this codebase
- Multi-language project: expect a frontend (HTML/CSS/JS) and a backend in Python talking to MySQL. Look for separate folders like `static/`, `templates/`, `server/`, `backend/`, or `web/` if added later.
- Database integration: MySQL connection details are likely provided via environment variables or a configuration file (`.env`, `config.py`, `settings.py`) — search for `DATABASE`, `DB_`, `MYSQL`, `DATABASE_URL`.

Concrete actions an agent should take when asked to implement or modify features
- If asked to run or test code: first locate the language manifest(s). If `requirements.txt` exists, create and activate a venv, install requirements, then run the main Python entry (common names: `app.py`, `main.py`, `server.py`). On Windows PowerShell:
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1
  - pip install -r requirements.txt
  - python app.py   # only if app.py exists
- If `package.json` exists (frontend tooling), use `npm ci` then `npm start` or `npm test` depending on scripts defined there.
- If there are no manifests, do NOT add assumptions about build tooling; instead prompt the repo owner: "Where are the application sources and what command starts the app/tests?"

Project-specific patterns to follow (based on discoverable content)
- Respect existing backup rules in `.specstory/` — edits to `.github/copilot-instructions.md` may be accompanied by automatic backups. Avoid noisy frequent rewrites.
- Keep changes minimal and explain them inline (short PR descriptions). This repo is coursework-focused; clear commit messages help instructors and graders.

When creating PRs or making edits
- Include a brief summary of what changed and a short list of manual test steps (how to start server, which page/route to open). If you added DB schema changes, include migration steps or sample SQL.
- If you add new files or folders, update `README.md` with a short section explaining how to run the project locally.

If something is missing or ambiguous (required prompt template)
- Use this exact prompt to the owner before implementing: "I couldn't find the application sources in this repository (only `README.md`, `LICENSE`, and `.specstory/` were present). Where are the frontend/backend sources, which branch contains them, and what commands should I run to build/start the app and tests?"

Files to reference while working
- `README.md` — project summary and primary clue about languages used.
- `.specstory/.what-is-this.md` — contains notes about backup behavior for this repo and agent artifacts.

Short change contract (when implementing a feature)
- Inputs: requested feature description and any provided spec or test case.
- Outputs: minimal working code, updated README with run steps, and a small test or verification steps.
- Error modes: if DB credentials or sources are missing, stop and ask the owner rather than guessing.

If you want to expand these instructions
- After the application sources are added to the repo, re-run a workspace scan and update this file with concrete entrypoints (filename(s)), exact run/test commands, and any custom linting or formatting rules found in the codebase.

Please review — if anything above is unclear or you expect other files to exist in this repo, tell me where the source lives (branch or path) and I will merge more precise instructions.
