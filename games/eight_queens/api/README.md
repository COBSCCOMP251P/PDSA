# Eight Queens API Endpoints

This directory contains the FastAPI route handlers for Eight Queens game.

## API Routes to Implement
- `POST /api/eight-queens/solve` - Solve the puzzle
- `GET /api/eight-queens/solutions/{n}` - Get all solutions for n-queens
- `POST /api/eight-queens/validate` - Validate a solution
- `GET /api/eight-queens/performance` - Get algorithm performance data

## Files to Create
- `routes.py` - Main API route definitions
- `models.py` - Pydantic models for requests/responses
- `utils.py` - Helper functions for API logic