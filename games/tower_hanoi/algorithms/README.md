# Tower of Hanoi: Interactive Game + Algorithm Benchmark

A comprehensive implementation of the Tower of Hanoi puzzle featuring an interactive web interface, multiple solving algorithms, and performance benchmarking capabilities.

## 🎯 Overview

This project combines the classic Tower of Hanoi puzzle with modern web technologies to create an educational platform that allows users to:

- Play interactive Tower of Hanoi games (3 or 4 pegs, 5-10 disks)
- Submit and validate their solutions
- Compete on a global leaderboard
- Compare their performance with 4 different algorithms
- Explore algorithm complexity and optimization techniques

## 🏗️ Architecture

### Frontend
- **HTML5/CSS3/JavaScript**: Modern, responsive web interface
- **Chart.js**: Interactive algorithm performance visualization
- **Vanilla JavaScript**: No framework dependencies for maximum compatibility

### Backend
- **FastAPI**: High-performance Python web framework
- **MySQL**: Relational database for persistent storage
- **Algorithm Engine**: 4 different Tower of Hanoi solving algorithms

### Algorithms Implemented
1. **Recursive 3-Peg**: Classic recursive solution (O(2^n) complexity)
2. **Iterative 3-Peg**: Stack-based iterative approach
3. **Frame-Stewart 4-Peg**: Optimal multi-peg algorithm
4. **Dynamic Programming 4-Peg**: Memoized optimization approach

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/COBSCCOMP251P/PDSA.git
   cd PDSA/games/tower_hanoi
   ```

2. **Set up the database**
   ```bash
   # Install MySQL and create database
   mysql -u root -p -e "CREATE DATABASE pdsa_games;"
   
   # Run migration script
   cd database
   ./migrate.sh root your_password localhost 3306
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Start the backend server**
   ```bash
   python main.py
   ```

6. **Open the frontend**
   ```bash
   cd ../frontend
   # Serve files using any HTTP server, e.g.:
   python -m http.server 3000
   # Open http://localhost:3000 in your browser
   ```

## 🎮 How to Play

### Starting a Round
1. Navigate to the "New Game" section
2. Choose between 3-peg or 4-peg configuration
3. Click "Create Random Round" to generate a puzzle with 5-10 disks

### Submitting Solutions
1. Enter your name
2. Declare how many moves you think it will take
3. Provide your move sequence in the format `A->B, A->C, B->C, ...`
4. Submit for validation and scoring

### Move Format
- Use `->` to indicate moves: `A->B` means "move top disk from peg A to peg B"
- Separate moves with commas, spaces, or newlines
- Example: `A->C, A->B, C->B, A->C, B->A, B->C, A->C`

## 📊 Algorithm Performance

The system automatically benchmarks 4 different algorithms for each round:

### 3-Peg Algorithms
- **Recursive**: Classic divide-and-conquer approach
- **Iterative**: Memory-efficient stack simulation

### 4-Peg Algorithms  
- **Frame-Stewart**: Provably optimal for most cases
- **Dynamic Programming**: Memoized optimization for smaller instances

Performance metrics include:
- Number of moves generated
- Runtime in milliseconds
- Memory usage patterns

## 🗄️ Database Schema

```sql
-- Core tables
CREATE TABLE players (id, name, created_at);
CREATE TABLE rounds (id, n_disks, peg_count, source, destination, started_at);
CREATE TABLE submissions (id, round_id, player_id, declared_moves, move_sequence, is_correct, validation_error, submitted_at);
CREATE TABLE algorithm_runs (id, round_id, algorithm_name, peg_count, computed_moves, runtime_ms, generated_sequence, run_at);

-- Performance view
CREATE VIEW leaderboard AS SELECT /* optimized leaderboard query */;
```

## 🧪 Testing

The project includes comprehensive test suites with >90% code coverage:

```bash
cd tests
pytest test_algorithms.py -v --cov=algorithms
pytest test_validator.py -v --cov=validator
```

### Test Coverage
- **Algorithm correctness**: Validates mathematical properties
- **Move validation**: Tests all game rules and edge cases  
- **API endpoints**: Integration tests for all REST endpoints
- **Performance**: Ensures algorithms complete within time bounds

## 📡 API Documentation

### Core Endpoints

#### Create Round
```http
POST /api/rounds
{
  "peg_count": 3,
  "n_disks": 7
}
```

#### Submit Solution
```http
POST /api/rounds/{id}/submit
{
  "player_name": "Alice",
  "declared_moves": 127,
  "move_sequence": ["A->C", "A->B", "C->B", ...]
}
```

#### Get Leaderboard
```http
GET /api/leaderboard?limit=10
```

#### Algorithm Results
```http
GET /api/rounds/{id}/algorithm-runs
```

### Response Formats
All endpoints return JSON with consistent error handling:
```json
{
  "correct": true,
  "errors": null,
  "saved_submission_id": 42,
  "validation_details": {...}
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_HOST=localhost
DATABASE_USER=root  
DATABASE_PASSWORD=secret
DATABASE_NAME=pdsa_games

# API
PORT=8000
DEBUG=true

# Performance
ALGORITHM_TIMEOUT=30
MAX_WORKERS=4
```

### Development vs Production
- **Development**: CORS allows all origins, debug logging enabled
- **Production**: Restrict CORS, disable debug, add rate limiting

## 🏆 Educational Value

This project demonstrates key computer science concepts:

### Algorithms & Data Structures
- **Recursion**: Classic recursive problem solving
- **Stack Simulation**: Converting recursion to iteration
- **Dynamic Programming**: Optimization through memoization
- **Complexity Analysis**: Comparing O(2^n) vs optimized approaches

### Software Engineering
- **API Design**: RESTful endpoints with proper HTTP semantics
- **Database Modeling**: Normalized schema with performance indexes
- **Testing**: Unit tests, integration tests, performance benchmarks
- **Documentation**: Comprehensive README, inline comments, API docs

### Performance Optimization
- **Algorithm Comparison**: Empirical analysis of different approaches
- **Memoization**: Trading memory for computation time
- **Database Optimization**: Indexes, views, query optimization

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend && python main.py

# Frontend  
cd frontend && python -m http.server 3000
```

### Production Deployment
```bash
# Use production WSGI server
pip install gunicorn
gunicorn main:app --workers 4 --bind 0.0.0.0:8000

# Serve frontend with nginx or Apache
# Configure reverse proxy for API calls
```

### Docker Deployment
```dockerfile
# Dockerfile example for backend
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-algorithm`
3. Make changes and add tests
4. Ensure all tests pass: `pytest`
5. Submit a pull request

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use modern ES6+ features
- **CSS**: Follow BEM methodology for class names

## 📚 Mathematical Background

### 3-Peg Tower of Hanoi
- **Minimum moves**: 2^n - 1 (proven optimal)
- **Recursive relation**: T(n) = 2×T(n-1) + 1
- **Growth rate**: Exponential O(2^n)

### 4-Peg Tower of Hanoi  
- **Frame-Stewart**: T(n) = min{2×T(k) + 2^(n-k) - 1} for k=1..n-1
- **Complexity**: Approximately O(2^√(2n))
- **Optimality**: Conjectured optimal, proven for n≤30

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Verify credentials in .env file
mysql -u root -p -e "SELECT 1;"
```

**CORS Errors in Browser**
```bash
# Ensure backend allows frontend origin
# Update ALLOWED_ORIGINS in .env
```

**Algorithm Timeouts**
```bash
# Increase ALGORITHM_TIMEOUT for large n
# Consider limiting max disk count
```

## 📄 License

MIT License - see LICENSE file for details.

## 👨‍💻 Authors

- **PDSA Team** - Initial implementation
- **Contributors** - See GitHub contributors

## 🙏 Acknowledgments

- Édouard Lucas - Original Tower of Hanoi puzzle (1883)
- Frame & Stewart - Multi-peg algorithm optimization
- FastAPI community - Excellent web framework
- Chart.js team - Beautiful data visualization

---

**Built with ❤️ for computer science education**
