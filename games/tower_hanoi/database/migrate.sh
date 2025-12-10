#!/bin/bash

# Tower of Hanoi Database Migration Script
# Usage: ./migrate.sh [mysql_user] [mysql_password] [mysql_host] [mysql_port]

set -e

# Default values
MYSQL_USER=${1:-root}
MYSQL_PASSWORD=${2:-""}
MYSQL_HOST=${3:-localhost}
MYSQL_PORT=${4:-3306}

echo "🏗️  Starting Tower of Hanoi database migration..."
echo "📍 Host: $MYSQL_HOST:$MYSQL_PORT"
echo "👤 User: $MYSQL_USER"

# Check if MySQL is accessible
echo "🔍 Checking MySQL connection..."
if ! mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "❌ Failed to connect to MySQL. Please check your credentials and server status."
    exit 1
fi

echo "✅ MySQL connection successful!"

# Run the schema migration
echo "📊 Creating database and tables..."
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < schema.sql

echo "✅ Database schema created successfully!"

# Insert some sample data for testing
echo "📝 Inserting sample data..."
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" pdsa_games << 'EOF'
-- Sample players
INSERT INTO players (name) VALUES 
('Alice'),
('Bob'),
('Charlie'),
('Diana');

-- Sample rounds
INSERT INTO rounds (n_disks, peg_count) VALUES 
(5, 3),
(6, 3),
(7, 4),
(8, 4);
EOF

echo "✅ Sample data inserted!"

# Verify the setup
echo "🔍 Verifying database setup..."
TABLES=$(mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" pdsa_games -e "SHOW TABLES;" | wc -l)
PLAYERS=$(mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" pdsa_games -e "SELECT COUNT(*) FROM players;" | tail -1)
ROUNDS=$(mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" pdsa_games -e "SELECT COUNT(*) FROM rounds;" | tail -1)

echo "📊 Database verification:"
echo "   - Tables created: $((TABLES - 1))"
echo "   - Sample players: $PLAYERS"
echo "   - Sample rounds: $ROUNDS"

echo "🎉 Migration completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "   1. Update your .env file with database credentials"
echo "   2. Start the backend API server"
echo "   3. Open the frontend in your browser"