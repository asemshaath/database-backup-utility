#!/bin/bash
set +e

echo "======================================"
echo "Postgres --> GCP Test"
echo "======================================"

# Start containers
echo "1. Starting containers..."

if docker-compose up -d --build --quiet > /dev/null 2>&1; then
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

echo "Setting up fake GCS..."

# Create bucket
docker-compose exec afterchive-host sh -c "
curl -s -X POST http://afterchive-gcs:4443/storage/v1/b \
  -H 'Content-Type: application/json' \
  -d '{\"name\":\"afterchive-test-bucket\"}'
"

# Verify bucket was created
BUCKET_CHECK=$(docker-compose exec afterchive-host sh -c "
curl -s http://afterchive-gcs:4443/storage/v1/b/afterchive-test-bucket
" | grep -c "afterchive-test-bucket" || echo "0")

if [ "$BUCKET_CHECK" -eq "0" ]; then
    echo "✗ FAILED: Could not create fake GCS bucket"
    docker-compose down -v
    exit 1
fi

echo "✓ Fake GCS bucket created"


echo "======================================"
echo "Test 1: Backup & Restore (CLI)"
echo "======================================"

# Backup
docker-compose exec afterchive-host afterchive backup \
    --db-type postgres \
    --db-host some-pg \
    --db-port 5432 \
    --db-pass 11 \
    --db-user testuser \
    --db-name testdb \
    --storage gcs \
    --bucket afterchive-test-bucket \
    --path ci-tests \
    --project test-project > /dev/null 2>&1

# Verify backup in GCS
GCS_RESPONSE=$(docker-compose exec afterchive-host sh -c "
curl -s http://afterchive-gcs:4443/storage/v1/b/afterchive-test-bucket/o
")

if ! echo "$GCS_RESPONSE" | grep -q "testdb"; then
    echo "✗ FAILED: No backup file in GCS"
    echo "GCS Response: $GCS_RESPONSE"
    docker-compose down -v
    exit 1
fi

echo "✓ Backup uploaded to GCS"

# Extract backup filename
BACKUP_FILE=$(echo "$GCS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'items' in data and len(data['items']) > 0:
    print(data['items'][0]['name'])
" | tr -d '\r\n')

if [ -z "$BACKUP_FILE" ]; then
    echo "✗ FAILED: Could not extract backup filename"
    docker-compose down -v
    exit 1
fi

BACKUP_FILENAME=$(basename "$BACKUP_FILE")
echo "Backup file: $BACKUP_FILENAME"

# Restore
docker-compose exec -T postgres psql -U testuser -d postgres \
    -c "DROP DATABASE IF EXISTS testdb_restored;" > /dev/null 2>&1
docker-compose exec -T postgres psql -U testuser -d postgres \
    -c "CREATE DATABASE testdb_restored;" > /dev/null 2>&1

docker-compose exec afterchive-host afterchive restore \
    --db-type postgres \
    --db-host some-pg \
    --db-port 5432 \
    --db-pass 11 \
    --db-user testuser \
    --db-name testdb_restored \
    --storage gcs \
    --bucket afterchive-test-bucket \
    --path ci-tests \
    --project test-project \
    --backup-file "$BACKUP_FILENAME" > /dev/null 2>&1

# Verify data
ORIGINAL_COUNT=$(docker-compose exec -T postgres psql -U testuser -d testdb -tAc "SELECT COUNT(*) FROM users;")
RESTORED_COUNT=$(docker-compose exec -T postgres psql -U testuser -d testdb_restored -tAc "SELECT COUNT(*) FROM users;")

if [ "$RESTORED_COUNT" != "$ORIGINAL_COUNT" ]; then
    echo "✗ FAILED: Data count mismatch (original: $ORIGINAL_COUNT, restored: $RESTORED_COUNT)"
    docker-compose down -v
    exit 1
fi

ORIGINAL_DATA=$(docker-compose exec -T postgres psql -U testuser -d testdb -tAc "SELECT username FROM users ORDER BY id;")
RESTORED_DATA=$(docker-compose exec -T postgres psql -U testuser -d testdb_restored -tAc "SELECT username FROM users ORDER BY id;")

if [ "$ORIGINAL_DATA" != "$RESTORED_DATA" ]; then
    echo "✗ FAILED: Data content mismatch"
    docker-compose down -v
    exit 1
fi

echo "✓ Restore successful ($RESTORED_COUNT users)"
echo "✓ Test 1 PASSED"
echo ""

# ===========================================
# TEST 2: Backup & Restore with YAML
# ===========================================

echo "======================================"
echo "Test 2: Backup & Restore (YAML)"
echo "======================================"

# Backup
docker-compose exec -e DB_PASSWORD=11 afterchive-host \
    afterchive backup --config /app/tests/fixtures/postgres-gcs.yaml > /dev/null 2>&1

# Get newest backup
GCS_RESPONSE=$(docker-compose exec afterchive-host sh -c "
curl -s http://afterchive-gcs:4443/storage/v1/b/afterchive-test-bucket/o
")

YAML_BACKUP_FILE=$(echo "$GCS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'items' in data and len(data['items']) > 0:
    # Get last item (most recent)
    print(data['items'][-1]['name'])
" | tr -d '\r\n')

YAML_BACKUP_FILENAME=$(basename "$YAML_BACKUP_FILE")
echo "✓ Backup created: $YAML_BACKUP_FILENAME"

# Restore
docker-compose exec -T postgres psql -U testuser -d postgres \
    -c "DROP DATABASE IF EXISTS testdb_restored_yaml;" > /dev/null 2>&1
docker-compose exec -T postgres psql -U testuser -d postgres \
    -c "CREATE DATABASE testdb_restored_yaml;" > /dev/null 2>&1




if ! docker-compose exec -e DB_PASSWORD=11 afterchive-host \
    afterchive restore \
    --config /app/tests/fixtures/postgres-gcs.yaml \
    --backup-file "$YAML_BACKUP_FILENAME" > /dev/null 2>&1; then
    echo "❌ FAILED: YAML restore command failed"
    docker-compose down -v
    exit 1
fi

# Verify
RESTORED_COUNT=$(docker-compose exec -T postgres psql -U testuser -d testdb_restored_yaml -tAc "SELECT COUNT(*) FROM users;")

if [ "$RESTORED_COUNT" != "$ORIGINAL_COUNT" ]; then
    echo "✗ FAILED: YAML restore data mismatch"
    docker-compose down -v
    exit 1
fi

ORIGINAL_DATA=$(docker-compose exec -T postgres psql -U testuser -d testdb -tAc "SELECT username FROM users ORDER BY id;")
RESTORED_DATA=$(docker-compose exec -T postgres psql -U testuser -d testdb_restored_yaml -tAc "SELECT username FROM users ORDER BY id;")

if [ "$ORIGINAL_DATA" != "$RESTORED_DATA" ]; then
    echo "✗ FAILED: YAML data content mismatch"
    docker-compose down -v
    exit 1
fi

echo "✓ Restore successful ($RESTORED_COUNT users)"
echo "✓ Test 2 PASSED"
echo ""


echo ""
echo "======================================"
echo "✓ ALL TESTS PASSED!"
echo "======================================"

# Cleanup
echo ""
echo "Cleaning up..."
docker-compose down -v

echo "✓ Done"

