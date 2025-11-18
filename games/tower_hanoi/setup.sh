#!/bin/bash

# Tower of Hanoi Game Setup Script
# Automates the setup process for local development

set -e

echo "🗼 Tower of Hanoi Game Setup"
echo "================================"

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

if ! python3 -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version is compatible"

# Check if MySQL is available
echo "🗄️  Checking MySQL availability..."
if command -v mysql >/dev/null 2>&1; then
    echo "✅ MySQL is installed"
else
    echo "❌ MySQL not found. Please install MySQL first:"
    echo "   macOS: brew install mysql"
    echo "   Ubuntu: sudo apt-get install mysql-server"
    echo "   Windows: Download from https://dev.mysql.com/downloads/"
    exit 1
fi

# Create virtual environment
echo "🌐 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
echo "✅ Backend dependencies installed"
cd ..

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Environment file created (.env)"
    echo "📝 Please edit .env with your MySQL credentials before running the server"
else
    echo "✅ Environment file already exists"
fi

# Database setup
echo "🗄️  Database setup..."
read -p "Do you want to set up the database now? (y/n): " setup_db

if [ "$setup_db" = "y" ] || [ "$setup_db" = "Y" ]; then
    read -p "MySQL username (default: root): " mysql_user
    mysql_user=${mysql_user:-root}
    
    read -s -p "MySQL password: " mysql_password
    echo
    
    read -p "MySQL host (default: localhost): " mysql_host
    mysql_host=${mysql_host:-localhost}
    
    echo "🔧 Running database migration..."
    cd database
    ./migrate.sh "$mysql_user" "$mysql_password" "$mysql_host"
    cd ..
    
    # Update .env file with actual credentials
    sed -i.bak "s/DATABASE_USER=root/DATABASE_USER=$mysql_user/" .env
    sed -i.bak "s/DATABASE_PASSWORD=your_mysql_password_here/DATABASE_PASSWORD=$mysql_password/" .env
    sed -i.bak "s/DATABASE_HOST=localhost/DATABASE_HOST=$mysql_host/" .env
    rm .env.bak
    
    echo "✅ Database setup completed"
else
    echo "⏭️  Database setup skipped"
fi

# Run tests
echo "🧪 Running tests..."
cd tests
if python -m pytest test_algorithms.py -v; then
    echo "✅ Algorithm tests passed"
else
    echo "⚠️  Some algorithm tests failed"
fi

if python -m pytest test_validator.py -v; then
    echo "✅ Validator tests passed"
else
    echo "⚠️  Some validator tests failed"
fi
cd ..

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Ensure your .env file has correct database credentials"
echo "2. Start the backend server:"
echo "   cd backend && python main.py"
echo "3. In another terminal, start the frontend:"
echo "   cd frontend && python -m http.server 3000"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "🚀 Happy coding!"