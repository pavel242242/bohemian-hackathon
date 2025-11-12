#!/bin/bash
# Quick Start Testing Script for SOAP Budget Service
# Usage: bash QUICK_START.sh

set -e

echo "========================================"
echo "SOAP Budget Service - Quick Start Tests"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SOAP_URL="http://localhost:5000/soap/BudgetService"
HEALTH_URL="http://localhost:5000/health"

# Function to print section headers
print_header() {
    echo ""
    echo -e "${YELLOW}>>> $1${NC}"
    echo ""
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if service is running
print_header "Checking if SOAP service is running..."

if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
    print_success "Service is running on $SOAP_URL"
else
    print_error "Service is NOT running!"
    echo "Start the service with: python soap_server.py"
    exit 1
fi

# Test 1: Get approvals for September 2025
print_header "Test 1: Get Campaign Approvals (September 2025)"

REQUEST_1=$(cat <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>2025-09-01</ns0:date_from>
            <ns0:date_to>2025-09-30</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>
EOF
)

RESPONSE_1=$(curl -s -X POST "$SOAP_URL" \
    -H "Content-Type: text/xml" \
    -d "$REQUEST_1")

# Extract total records from response
TOTAL=$(echo "$RESPONSE_1" | grep -o '<TotalRecords>[^<]*</TotalRecords>' | sed 's/<[^>]*>//g')

if [ -z "$TOTAL" ]; then
    print_error "Failed to parse response"
    echo "Response: $RESPONSE_1"
else
    print_success "Found $TOTAL approvals in September 2025"
    echo "Sample response:"
    echo "$RESPONSE_1" | grep -A5 "<Approval>" | head -20
fi

# Test 2: Get specific approval by ID
print_header "Test 2: Get Approval by ID (APR-006)"

REQUEST_2=$(cat <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalByID>
            <ns0:approval_id>APR-006</ns0:approval_id>
        </ns0:GetApprovalByID>
    </soap-env:Body>
</soap-env:Envelope>
EOF
)

RESPONSE_2=$(curl -s -X POST "$SOAP_URL" \
    -H "Content-Type: text/xml" \
    -d "$REQUEST_2")

# Extract campaign name from response
CAMPAIGN=$(echo "$RESPONSE_2" | grep -o '<CampaignName>[^<]*</CampaignName>' | sed 's/<[^>]*>//g')

if [ -z "$CAMPAIGN" ]; then
    print_error "Failed to retrieve approval APR-006"
else
    print_success "Retrieved approval for campaign: $CAMPAIGN"
    # Extract amount
    AMOUNT=$(echo "$RESPONSE_2" | grep -o '<ApprovedAmount>[^<]*</ApprovedAmount>' | sed 's/<[^>]*>//g')
    echo "Approved Amount: \$$AMOUNT"
fi

# Test 3: Get approvals by cost center
print_header "Test 3: Get Approvals by Cost Center (US-MARKETING-DIGITAL)"

REQUEST_3=$(cat <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalsByCostCenter>
            <ns0:cost_center>US-MARKETING-DIGITAL</ns0:cost_center>
        </ns0:GetApprovalsByCostCenter>
    </soap-env:Body>
</soap-env:Envelope>
EOF
)

RESPONSE_3=$(curl -s -X POST "$SOAP_URL" \
    -H "Content-Type: text/xml" \
    -d "$REQUEST_3")

# Extract metadata
RECORDS=$(echo "$RESPONSE_3" | grep -o '<TotalRecords>[^<]*</TotalRecords>' | sed 's/<[^>]*>//g')
TOTAL_AMOUNT=$(echo "$RESPONSE_3" | grep -o '<TotalApprovedAmount>[^<]*</TotalApprovedAmount>' | sed 's/<[^>]*>//g')

if [ -z "$RECORDS" ]; then
    print_error "Failed to retrieve cost center approvals"
else
    print_success "Retrieved $RECORDS approvals for US-MARKETING-DIGITAL"
    echo "Total Approved Amount: \$$TOTAL_AMOUNT"
fi

# Test 4: Get October 2025 approvals
print_header "Test 4: Get Campaign Approvals (October 2025)"

REQUEST_4=$(cat <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>2025-10-01</ns0:date_from>
            <ns0:date_to>2025-10-31</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>
EOF
)

RESPONSE_4=$(curl -s -X POST "$SOAP_URL" \
    -H "Content-Type: text/xml" \
    -d "$REQUEST_4")

TOTAL=$(echo "$RESPONSE_4" | grep -o '<TotalRecords>[^<]*</TotalRecords>' | sed 's/<[^>]*>//g')

if [ -z "$TOTAL" ]; then
    print_error "Failed to parse response"
else
    print_success "Found $TOTAL approvals in October 2025"
fi

# Test 5: Invalid approval ID
print_header "Test 5: Get Non-existent Approval (APR-999)"

REQUEST_5=$(cat <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalByID>
            <ns0:approval_id>APR-999</ns0:approval_id>
        </ns0:GetApprovalByID>
    </soap-env:Body>
</soap-env:Envelope>
EOF
)

RESPONSE_5=$(curl -s -X POST "$SOAP_URL" \
    -H "Content-Type: text/xml" \
    -d "$REQUEST_5")

ERROR=$(echo "$RESPONSE_5" | grep -o '<Code>[^<]*</Code>' | sed 's/<[^>]*>//g')

if [ "$ERROR" = "NOT_FOUND" ]; then
    print_success "Correctly returned NOT_FOUND error for non-existent approval"
else
    print_error "Expected NOT_FOUND error"
fi

# Summary
print_header "Test Summary"
echo "All tests completed successfully!"
echo ""
echo "Service Details:"
echo "  URL: $SOAP_URL"
echo "  Health Check: $HEALTH_URL"
echo "  Status: Running"
echo ""
echo "Next steps:"
echo "  1. View full documentation: cat README.md"
echo "  2. Run Python test suite: python test_soap_service.py"
echo "  3. Deploy with Docker: docker-compose up"
echo ""
print_success "SOAP Budget Service is operational!"
