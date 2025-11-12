#!/bin/bash

# STAGEHAND Mock Servers Test Script
# Tests all 4 mock servers to verify they're working

echo "=========================================="
echo "STAGEHAND Mock Servers Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}

    echo -n "Testing $name... "

    if [ "$method" = "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" 2>/dev/null)
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    fi

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to test with data preview
test_with_preview() {
    local name=$1
    local url=$2
    local method=${3:-GET}

    echo ""
    echo "=========================================="
    echo "$name"
    echo "=========================================="

    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$url" -H "Content-Type: application/json" 2>/dev/null)
    else
        response=$(curl -s "$url" 2>/dev/null)
    fi

    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}✓ Connected successfully${NC}"
        echo ""
        echo "Sample response:"
        echo "$response" | python3 -m json.tool 2>/dev/null | head -30
        echo ""
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ Failed to connect${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "Starting tests..."
echo ""

# Test 1: Meta Ad Library Mock
test_with_preview "1. Meta Ad Library Mock (port 3001)" "http://localhost:3001/ads_archive"

# Test 2: Google Ads Mock
test_with_preview "2. Google Ads Mock (port 8000)" "http://localhost:8000/health"

# Test 3: TikTok Ads Mock
test_with_preview "3. TikTok Ads Mock (port 3003)" "http://localhost:3003/health"

# Test 4: SOAP Budget Mock
echo ""
echo "=========================================="
echo "4. SOAP Budget Mock (port 5001)"
echo "=========================================="
response=$(curl -s "http://localhost:5001/health" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$response" ]; then
    echo -e "${GREEN}✓ SOAP server is running${NC}"
    echo "Response: $response"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ SOAP server not responding${NC}"
    ((TESTS_FAILED++))
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All mock servers are working!${NC}"
    echo ""
    echo "You can now test the backend:"
    echo "  cd backend && npm run dev"
    echo ""
    echo "And the UI:"
    echo "  cd ui && npm run dev"
    exit 0
else
    echo -e "${YELLOW}⚠ Some servers are not running${NC}"
    echo ""
    echo "To start servers:"
    echo "  Meta:       cd mocks/meta-api && npm start"
    echo "  Google:     cd mocks/google-ads && python server.py"
    echo "  TikTok:     cd mocks/tiktok-api && npm start"
    echo "  SOAP:       cd mocks/soap-budget && python soap_server.py"
    exit 1
fi
