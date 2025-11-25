#!/bin/bash
set -e

echo "======================================"
echo "Starting Afterchive Tests"
echo "======================================"

# Start containers
echo "1. Starting containers..."

if docker-compose up -d --build; then
    echo "✓ Containers started"
else
    echo "✗ FAILED to start containers"
    exit 1
fi

# Wait for Postgres to be ready
echo "Waiting for Postgres to be ready..."
sleep 5

# Load test database
echo "2. Loading test database from pgtest.sql..."

if docker-compose exec -T postgres psql -U testuser -d testdb < fixtures/pgtest.sql > /dev/null; then
    echo "✓ Test database loaded"
else
    echo "✗ FAILED to load test database"
    docker-compose down -v
    exit 1
fi


# Verify test data
echo ""
echo "Database contents:"
docker-compose exec -T postgres psql -U testuser -d testdb -c "
SELECT 'Users: ' || COUNT(*) FROM users
UNION ALL
SELECT 'Posts: ' || COUNT(*) FROM posts
UNION ALL
SELECT 'Comments: ' || COUNT(*) FROM comments;
"

# Test 1: Backup with CLI flags
echo ""
echo "======================================"
echo "Test 1: Backup with CLI flags PG --> Local"
echo "======================================"

docker-compose exec afterchive-host afterchive backup \
    --db-type postgres \
    --db-host some-pg \
    --db-port 5432 \
    --db-pass 11 \
    --db-user testuser \
    --db-name testdb \
    --storage local \
    --path /tmp/backups > /dev/null


# Check if backup file was created
BACKUP_COUNT=$(docker-compose exec afterchive-host sh -c "ls /tmp/backups/*.sql 2>/dev/null | wc -l")

if [ "$BACKUP_COUNT" -eq "0" ]; then
    echo "✗ Test 1 FAILED: No backup file created"
    exit 1
fi

echo "✓ Backup file created"

BACKUP_FILE=$(docker-compose exec afterchive-host ls -t /tmp/backups/ | grep testdb | head -n1 | tr -d '\r\n')
echo "Backup file: $BACKUP_FILE"

BACKUP_SIZE=$(docker-compose exec afterchive-host sh -c "stat -c%s /tmp/backups/$BACKUP_FILE")
echo "Backup size: $BACKUP_SIZE"

if [ "$BACKUP_SIZE" -lt 100 ]; then
    echo "✗ Test 1 FAILED: Backup file size too small"
    exit 1
fi


echo "✓ Test 1 PASSED"

echo ""
echo "======================================="
echo "Test2: test backup with wrong db password"
echo "======================================="

if docker-compose exec afterchive-host afterchive backup \
    --db-type postgres \
    --db-host some-pg \
    --db-port 5432 \
    --db-pass WRONGPASSWORD \
    --db-user testuser \
    --db-name testdb \
    --storage local \
    --path /tmp/backups 2>&1 | grep -q "Authentication failed"; then
    echo "✓ Test 2 PASSED (correctly rejected wrong password)"
else
    echo "✗ FAILED (should have rejected wrong password)"
    docker-compose down -v
    exit 1
fi

echo ""
echo "======================================="
echo "Test3: test backup with unreachable DB host"
echo "======================================="

if docker-compose exec afterchive-host afterchive backup \
    --db-type postgres \
    --db-host invalid-host \
    --db-port 5432 \
    --db-pass 11 \
    --db-user testuser \
    --db-name testdb \
    --storage local \
    --path /tmp/backups 2>&1 | grep -q "could not translate host name"; then
    echo "✓ Test 3 PASSED (correctly handled unreachable host)"
else
    echo "✗ FAILED (should have handled unreachable host)"
    docker-compose down -v
    exit 1
fi


echo ""
echo "======================================"
echo "Test4: test backup with missing arguments"
echo "======================================"

# docker-compose exec afterchive-host afterchive backup \
#     --db-type postgres \
#     --storage local

if docker-compose exec afterchive-host afterchive backup \
    --db-type postgres \
    --storage local 2>&1 | grep -q "required"; then
    echo "✓ Test 4 PASSED (correctly handled missing argument)"
else
    echo "✗ FAILED (should have handled missing argument)"
    docker-compose down -v
    exit 1
fi

echo ""
echo "======================================"
echo "Test5: Backup with YAML config PG --> Local"
echo "======================================"

if ! docker-compose exec -e DB_PASSWORD=11 afterchive-host afterchive backup --config tests/fixtures/pgtest.yaml > /dev/null 2>&1; then
    echo "✗ Test 5 FAILED: Backup command failed"
    docker-compose down -v
    exit 1
fi

# Check if backup file was created
BACKUP_COUNT=$(docker-compose exec afterchive-host sh -c "ls /tmp/backups/*.sql 2>/dev/null | wc -l")

if [ "$BACKUP_COUNT" -eq "0" ]; then
    echo "✗ Test 5 FAILED: No backup file created"
    exit 1
fi

echo "✓ Backup file created"

BACKUP_FILE=$(docker-compose exec afterchive-host sh -c "ls -t /tmp/backups/ | head -n1" | tr -d '\r')
echo "Backup file: $BACKUP_FILE"


BACKUP_SIZE=$(docker-compose exec afterchive-host sh -c "stat -c%s /tmp/backups/$BACKUP_FILE")
echo "Backup size: $BACKUP_SIZE"

if [ "$BACKUP_SIZE" -lt 100 ]; then
    echo "✗ Test 5 FAILED: Backup file size too small"
    exit 1
fi


echo "✓ Test 5 PASSED"


echo ""
echo "======================================"
echo "✓ ALL TESTS PASSED!"
echo "======================================"

# Cleanup
echo ""
echo "Cleaning up..."
docker-compose down -v

echo "✓ Done"


# ============= FOR FUTURE TESTS =============
# =========================================================================================================

# # Test 2: Backup with YAML config
# echo ""
# echo "======================================"
# echo "Test 2: Backup with YAML config"
# echo "======================================"
# docker-compose exec afterchive python /app/core/cli.py backup \
#     --config /app/test-config.yaml

# echo "✓ Test 2 passed"

# # List backup files
# echo ""
# echo "Backup files created:"
# docker-compose exec afterchive ls -lh /tmp/backups/

# # Test 3: Restore
# echo ""
# echo "======================================"
# echo "Test 3: Restore to new database"
# echo "======================================"

# BACKUP_FILE=$(docker-compose exec afterchive ls /tmp/backups/ | grep testdb | head -n 1 | tr -d '\r')

# echo "Restoring from: $BACKUP_FILE"

# docker-compose exec afterchive python /app/core/cli.py restore \
#     --config /app/test-config.yaml \
#     --backup-file "$BACKUP_FILE"

# echo "✓ Test 3 passed"

# # Verify restored data
# echo ""
# echo "======================================"
# echo "Verifying restored data..."
# echo "======================================"
# docker-compose exec -T postgres psql -U testuser -d testdb_restored -c "
# SELECT 'Users: ' || COUNT(*) FROM users
# UNION ALL
# SELECT 'Posts: ' || COUNT(*) FROM posts
# UNION ALL
# SELECT 'Comments: ' || COUNT(*) FROM comments;
# "

# echo ""
# echo "Sample data from restored database:"
# docker-compose exec -T postgres psql -U testuser -d testdb_restored -c "SELECT * FROM users LIMIT 3;"

# echo ""
# echo "======================================"
# echo "✓ ALL TESTS PASSED!"
# echo "======================================"

# # Cleanup
# echo ""
# echo "Cleaning up..."
# docker-compose down -v

# echo "✓ Done"
# ```

# ---

