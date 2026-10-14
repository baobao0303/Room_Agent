#!/usr/bin/env bash
set -e

echo "=== Setting up Harness for Paseo Project (Floci Cloud Storage) ==="

# 1. Check prerequisites
for cmd in curl git; do
    if ! command -v $cmd &> /dev/null; then
        echo "Missing required command: $cmd"
        exit 1
    fi
done

# 2. Configure environment
if [ ! -f .env ]; then
    echo "--> Initializing .env configuration..."
    cat << 'EOF' > .env
HARNESS_MODEL=gemini-3.7-medium
HARNESS_BACKEND=floci
FLOCI_ENDPOINT=http://<FLOCI_HOST>:14566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=floci_local_key
AWS_SECRET_ACCESS_KEY=floci_local_secret
FLOCI_S3_BUCKET=harness-data
HARNESS_LOG_LEVEL=info
EOF
fi

# 3. Initialize Floci DynamoDB & S3 infrastructure
echo "--> Initializing Floci DynamoDB tables & S3 bucket..."
chmod +x ./scripts/harness || true
./scripts/harness init

# 4. Seed sample data
echo "--> Seeding sample stories and tools..."
./scripts/harness seed

# 5. Verify installation
echo "--> Verifying database tables..."
./scripts/harness query stats
./scripts/harness query matrix

echo ""
echo "=== Harness Setup on Floci Completed Successfully! ==="
