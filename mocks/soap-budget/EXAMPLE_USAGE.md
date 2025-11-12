# SOAP Budget Service - Example Usage Guide

Complete working examples for testing the SOAP Budget Approval Service.

## Table of Contents

1. [Setup](#setup)
2. [Example 1: Get September Approvals](#example-1-get-september-approvals)
3. [Example 2: Get Single Approval](#example-2-get-single-approval)
4. [Example 3: Get Cost Center Summary](#example-3-get-cost-center-summary)
5. [Example 4: Date Range Queries](#example-4-date-range-queries)
6. [Example 5: Error Handling](#example-5-error-handling)
7. [Using Different Tools](#using-different-tools)
8. [Integration Patterns](#integration-patterns)

## Setup

### Start the Service

```bash
# Navigate to directory
cd /Users/chocho/projects/STAGEHAND/mocks/soap-budget

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the service
python soap_server.py
```

You should see:
```
Starting SOAP Budget Service on http://localhost:5000
WSDL available at: http://localhost:5000/soap/BudgetService?wsdl
WARNING in app.run, running with debugger enabled.
```

### Verify Service is Running

```bash
curl http://localhost:5000/health
# Response: {"status": "healthy"}
```

## Example 1: Get September Approvals

This example retrieves all approvals that were approved in September 2025.

### Request

```xml
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
```

### Using curl

```bash
cat > request.xml << 'EOF'
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

curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d @request.xml | xmllint --format -
```

### Response (Formatted)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GetCampaignApprovalsResponse>
    <Metadata>
        <TotalRecords>15</TotalRecords>
        <DateFrom>2025-09-01</DateFrom>
        <DateTo>2025-09-30</DateTo>
        <QueryTimestamp>2025-11-11T10:45:32.123456</QueryTimestamp>
    </Metadata>
    <Approvals>
        <Approval>
            <ApprovalID>APR-001</ApprovalID>
            <CampaignID>AirMaxDay</CampaignID>
            <CampaignName>Air Max Day Campaign</CampaignName>
            <ApprovedAmount>2250000.0</ApprovedAmount>
            <Currency>USD</Currency>
            <CostCenter>US-MARKETING-DIGITAL</CostCenter>
            <ApprovalDate>2025-09-01</ApprovalDate>
            <EffectiveDate>2025-09-15</EffectiveDate>
            <ApproverName>Sarah Johnson</ApproverName>
            <ApproverEmail>sarah.johnson@company.com</ApproverEmail>
            <Status>APPROVED</Status>
            <Notes>Q3 summer campaign launch</Notes>
        </Approval>
        <Approval>
            <ApprovalID>APR-002</ApprovalID>
            <CampaignID>NikeByYou</CampaignID>
            <CampaignName>Nike By You Customization Campaign</CampaignName>
            <ApprovedAmount>1100000.0</ApprovedAmount>
            <Currency>USD</Currency>
            <CostCenter>US-MARKETING-DIGITAL</CostCenter>
            <ApprovalDate>2025-09-06</ApprovalDate>
            <EffectiveDate>2025-09-20</EffectiveDate>
            <ApproverName>Michael Chen</ApproverName>
            <ApproverEmail>michael.chen@company.com</ApproverEmail>
            <Status>APPROVED</Status>
            <Notes>Product customization feature promotion</Notes>
        </Approval>
        <!-- ... 13 more approvals ... -->
    </Approvals>
</GetCampaignApprovalsResponse>
```

### What This Shows

- **TotalRecords: 15** - 15 approvals were approved in September
- Each approval includes complete details
- Data is returned in chronological order
- Query timestamp shows server response time

## Example 2: Get Single Approval

This example retrieves a specific approval by its ID.

### Request

```xml
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
```

### Using curl

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalByID>
            <ns0:approval_id>APR-006</ns0:approval_id>
        </ns0:GetApprovalByID>
    </soap-env:Body>
</soap-env:Envelope>'
```

### Response

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GetApprovalByIDResponse>
    <Approval>
        <ApprovalID>APR-006</ApprovalID>
        <CampaignID>JustDoIt</CampaignID>
        <CampaignName>Just Do It Fitness Initiative</CampaignName>
        <ApprovedAmount>1650000.0</ApprovedAmount>
        <Currency>USD</Currency>
        <CostCenter>GLOBAL-BRAND</CostCenter>
        <ApprovalDate>2025-09-23</ApprovalDate>
        <EffectiveDate>2025-10-05</EffectiveDate>
        <ApproverName>Robert Thompson</ApproverName>
        <ApproverEmail>robert.thompson@company.com</ApproverEmail>
        <Status>APPROVED</Status>
        <Notes>Brand purpose campaign - fitness and wellness</Notes>
    </Approval>
</GetApprovalByIDResponse>
```

### Use Cases

- Lookup approval details for a specific budget request
- Get approver information
- Verify approval status
- Check effective dates for financial reporting

## Example 3: Get Cost Center Summary

This example retrieves all approvals for a specific cost center with aggregated totals.

### Request

```xml
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
```

### Using curl

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalsByCostCenter>
            <ns0:cost_center>US-MARKETING-DIGITAL</ns0:cost_center>
        </ns0:GetApprovalsByCostCenter>
    </soap-env:Body>
</soap-env:Envelope>'
```

### Response

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GetApprovalsByCostCenterResponse>
    <Metadata>
        <CostCenter>US-MARKETING-DIGITAL</CostCenter>
        <TotalRecords>12</TotalRecords>
        <TotalApprovedAmount>21930000.0</TotalApprovedAmount>
    </Metadata>
    <Approvals>
        <Approval>
            <ApprovalID>APR-001</ApprovalID>
            <CampaignID>AirMaxDay</CampaignID>
            <CampaignName>Air Max Day Campaign</CampaignName>
            <ApprovedAmount>2250000.0</ApprovedAmount>
            <Currency>USD</Currency>
            <CostCenter>US-MARKETING-DIGITAL</CostCenter>
            <ApprovalDate>2025-09-01</ApprovalDate>
            <EffectiveDate>2025-09-15</EffectiveDate>
            <ApproverName>Sarah Johnson</ApproverName>
            <Status>APPROVED</Status>
        </Approval>
        <!-- ... 11 more approvals ... -->
    </Approvals>
</GetApprovalsByCostCenterResponse>
```

### Key Points

- **TotalRecords: 12** - 12 approvals for this cost center
- **TotalApprovedAmount: 21,930,000** - Total budget for cost center
- Includes individual approval records for detailed breakdown
- Useful for cost center budget reporting and forecasting

## Example 4: Date Range Queries

Different date ranges for various reporting needs.

### All Approvals (Full Range)

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>2025-08-01</ns0:date_from>
            <ns0:date_to>2025-12-31</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>'
```

Result: **20 total approvals** across all available dates

### August Only

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>2025-08-01</ns0:date_from>
            <ns0:date_to>2025-08-31</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>'
```

Result: **3 approvals** (Aug 18, 20, 25)

### October Only

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>2025-10-01</ns0:date_from>
            <ns0:date_to>2025-10-31</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>'
```

Result: **4 approvals** (Oct 15, 20, 25, + 1 from Nov scheduled in Oct)

## Example 5: Error Handling

### Query Non-existent Approval

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalByID>
            <ns0:approval_id>APR-999</ns0:approval_id>
        </ns0:GetApprovalByID>
    </soap-env:Body>
</soap-env:Envelope>'
```

### Response (Error)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>NOT_FOUND</Code>
    <Message>Approval APR-999 not found</Message>
</Error>
```

### Invalid Date Format

```bash
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>09/01/2025</ns0:date_from>
            <ns0:date_to>09/30/2025</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>'
```

### Response (Error)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Error>Invalid date format. Use YYYY-MM-DD: time data '09/01/2025' does not match format '%Y-%m-%d'</Error>
```

## Using Different Tools

### Using Python

```python
import requests
from lxml import etree

# SOAP request
request_xml = """<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>2025-09-01</ns0:date_from>
            <ns0:date_to>2025-09-30</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>"""

# Send request
response = requests.post(
    'http://localhost:5000/soap/BudgetService',
    data=request_xml,
    headers={'Content-Type': 'text/xml'}
)

# Parse response
root = etree.fromstring(response.content)
total = root.findtext('.//TotalRecords')
print(f"Found {total} approvals")

# Extract individual approvals
for approval in root.findall('.//Approval'):
    campaign = approval.findtext('CampaignName')
    amount = approval.findtext('ApprovedAmount')
    print(f"  - {campaign}: ${amount}")
```

### Using Postman

1. Create new POST request
2. URL: `http://localhost:5000/soap/BudgetService`
3. Headers tab: Add `Content-Type: text/xml`
4. Body tab (raw): Paste one of the SOAP examples
5. Click Send
6. Response appears in lower panel

### Using SoapUI

1. Create new SOAP project
2. WSDL: `http://localhost:5000/soap/BudgetService?wsdl`
3. Auto-generates request templates
4. Fill in parameters
5. Right-click method name, select "Show request"

## Integration Patterns

### Pattern 1: Budget Approval Dashboard

Retrieve approvals for current month:

```python
from datetime import datetime, timedelta
import requests
from lxml import etree

today = datetime.now()
month_start = today.replace(day=1).strftime('%Y-%m-%d')
month_end = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
month_end = month_end.strftime('%Y-%m-%d')

request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetCampaignApprovals>
            <ns0:date_from>{month_start}</ns0:date_from>
            <ns0:date_to>{month_end}</ns0:date_to>
        </ns0:GetCampaignApprovals>
    </soap-env:Body>
</soap-env:Envelope>"""

response = requests.post(
    'http://localhost:5000/soap/BudgetService',
    data=request_xml,
    headers={'Content-Type': 'text/xml'}
)

# Parse and display results
root = etree.fromstring(response.content)
print(f"Month {month_start} to {month_end}:")
print(f"Total Approvals: {root.findtext('.//TotalRecords')}")
```

### Pattern 2: Cost Center Budget Report

Generate budget report by cost center:

```python
import requests
from lxml import etree

cost_centers = ['US-MARKETING-DIGITAL', 'GLOBAL-BRAND']

for cc in cost_centers:
    request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalsByCostCenter>
            <ns0:cost_center>{cc}</ns0:cost_center>
        </ns0:GetApprovalsByCostCenter>
    </soap-env:Body>
</soap-env:Envelope>"""

    response = requests.post(
        'http://localhost:5000/soap/BudgetService',
        data=request_xml,
        headers={'Content-Type': 'text/xml'}
    )

    root = etree.fromstring(response.content)
    count = root.findtext('.//TotalRecords')
    total = root.findtext('.//TotalApprovedAmount')

    print(f"{cc}:")
    print(f"  Records: {count}")
    print(f"  Total: ${float(total):,.2f}")
```

### Pattern 3: Approval Verification

Verify approval before processing:

```python
import requests
from lxml import etree

def verify_approval(approval_id):
    request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope
    xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns0="http://company.example.com/budget/approval">
    <soap-env:Body>
        <ns0:GetApprovalByID>
            <ns0:approval_id>{approval_id}</ns0:approval_id>
        </ns0:GetApprovalByID>
    </soap-env:Body>
</soap-env:Envelope>"""

    response = requests.post(
        'http://localhost:5000/soap/BudgetService',
        data=request_xml,
        headers={'Content-Type': 'text/xml'}
    )

    root = etree.fromstring(response.content)
    status = root.findtext('.//Status')
    amount = root.findtext('.//ApprovedAmount')

    if status == 'APPROVED':
        return True, amount
    else:
        return False, None

# Usage
is_approved, amount = verify_approval('APR-006')
if is_approved:
    print(f"Approval confirmed. Amount: ${amount}")
else:
    print("Approval not found or rejected")
```

## Summary

All examples work with the running SOAP service. Key points:

- All requests must be valid XML
- Dates must be in YYYY-MM-DD format
- Cost center codes are case-sensitive
- Approval IDs are case-sensitive (APR-001 not apr-001)
- Responses include query metadata
- Error responses are XML formatted
- Service is stateless (no session management needed)

For more details, see the full [README.md](README.md).
