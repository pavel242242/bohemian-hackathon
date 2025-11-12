#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:4000"
MOCK_SERVER_URL="http://localhost:3001"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}STAGEHAND Backend Integration Test${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
echo "GET $BACKEND_URL/health"
response=$(curl -s "$BACKEND_URL/health")
if echo "$response" | grep -q "ok"; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "Response: $response\n"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "Response: $response\n"
fi

# Test 2: Meta Mock Server Status
echo -e "${YELLOW}Test 2: Meta Mock Server Status${NC}"
echo "GET $MOCK_SERVER_URL/ads_archive"
response=$(curl -s -w "\n%{http_code}" "$MOCK_SERVER_URL/ads_archive")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ]; then
  echo -e "${GREEN}✓ Mock server is running${NC}"
  echo "Response: $body\n"
else
  echo -e "${YELLOW}⚠ Mock server not responding (HTTP $http_code)${NC}"
  echo "Response: $body\n"
fi

# Test 3: Query Campaigns (basic)
echo -e "${YELLOW}Test 3: Query Campaigns (Basic)${NC}"
echo "GET $BACKEND_URL/api/campaigns"
response=$(curl -s "$BACKEND_URL/api/campaigns")
if echo "$response" | grep -q "success"; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "Response: $response\n"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "Response: $response\n"
fi

# Test 4: Query Campaigns with Search
echo -e "${YELLOW}Test 4: Query Campaigns with Search${NC}"
echo "GET $BACKEND_URL/api/campaigns?search=test"
response=$(curl -s "$BACKEND_URL/api/campaigns?search=test")
if echo "$response" | grep -q "success"; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "Response: $response\n"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "Response: $response\n"
fi

# Test 5: Query Campaigns with Limit
echo -e "${YELLOW}Test 5: Query Campaigns with Limit${NC}"
echo "GET $BACKEND_URL/api/campaigns?limit=5"
response=$(curl -s "$BACKEND_URL/api/campaigns?limit=5")
if echo "$response" | grep -q "success"; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "Response: $response\n"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "Response: $response\n"
fi

# Test 6: Direct Ads Archive Query
echo -e "${YELLOW}Test 6: Direct Ads Archive Query${NC}"
echo "GET $BACKEND_URL/api/ads_archive"
response=$(curl -s "$BACKEND_URL/api/ads_archive")
if echo "$response" | grep -q "success"; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "Response: $response\n"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "Response: $response\n"
fi

# Test 7: 404 Error Handling
echo -e "${YELLOW}Test 7: 404 Error Handling${NC}"
echo "GET $BACKEND_URL/nonexistent"
response=$(curl -s "$BACKEND_URL/nonexistent")
if echo "$response" | grep -q "success.*false"; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "Response: $response\n"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "Response: $response\n"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
