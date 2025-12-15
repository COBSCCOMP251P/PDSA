# Traveling Salesman Tests

Unit tests for the algorithms live in `backend/tests/test_algorithms.py` and use `pytest`.

Run them with:
```bash
cd games/traveling_salesman
pytest backend/tests
```

The tests assert:
- Brute force returns the optimal distance for small sets.
- Nearest neighbor visits each city once and returns home.
- Dynamic programming distance matches brute force for a shared matrix.
- Scoring helper stays within 10–100.
