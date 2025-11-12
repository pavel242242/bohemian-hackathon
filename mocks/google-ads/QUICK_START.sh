#!/bin/bash

# Google Ads API Mock Server - Quick Start Script
# This script provides quick commands to test the mock server

set -e

echo "Google Ads API Mock Server - Quick Start"
echo "========================================"
echo ""

# Check if server is running
SERVER_URL="http://localhost:8000"

check_server() {
    if curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Test the server
run_tests() {
    echo "Running tests..."
    echo ""

    echo "1. Health Check:"
    curl -s "$SERVER_URL/health" | python -m json.tool
    echo ""

    echo "2. List All Campaigns:"
    curl -s "$SERVER_URL/campaigns" | python -c "import sys, json; d=json.load(sys.stdin); print(f\"Found {d['count']} campaigns\")"
    echo ""

    echo "3. List YouTube Campaigns:"
    curl -s "$SERVER_URL/campaigns?channel=YouTube" | python -c "import sys, json; d=json.load(sys.stdin); [print(f\"  - {c['name']}\") for c in d['campaigns']]"
    echo ""

    echo "4. Google Ads API Search (First 2 campaigns):"
    curl -s -X POST "$SERVER_URL/googleads/v16/customers/1234567890/googleAds:search" | \
        python -c "import sys, json; d=json.load(sys.stdin); [print(f\"  {r['campaign']['name']}: {r['metrics']['impressions']} impressions\") for r in d['results'][:2]]"
    echo ""

    echo "5. Search with Date Filter (Oct 1 - Nov 11):"
    curl -s -X POST "$SERVER_URL/googleads/v16/customers/1234567890/googleAds:search?start_date=2025-10-01&end_date=2025-11-11" | \
        python -c "import sys, json; d=json.load(sys.stdin); print(f\"Found {d['totalResultsCount']} campaigns in date range\")"
    echo ""

    echo "Tests completed successfully!"
}

# Main script
if ! check_server; then
    echo "ERROR: Server is not running at $SERVER_URL"
    echo ""
    echo "Start the server with:"
    echo "  python /Users/chocho/projects/STAGEHAND/mocks/google-ads/server.py"
    echo ""
    echo "Or using Docker:"
    echo "  docker build -t google-ads-mock:latest /Users/chocho/projects/STAGEHAND/mocks/google-ads/"
    echo "  docker run -p 8000:8000 google-ads-mock:latest"
    echo ""
    exit 1
fi

run_tests

echo ""
echo "For more examples, see TEST_EXAMPLES.md"
