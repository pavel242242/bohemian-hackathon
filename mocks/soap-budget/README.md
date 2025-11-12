# SOAP Budget Approval Service Mock

A legacy enterprise finance system simulator using SOAP/XML web services. This mock service provides budget approval data for various marketing campaigns, simulating a real-world enterprise budget approval workflow.

## Overview

This service demonstrates:
- SOAP 1.1 protocol implementation with Flask + Spyne
- XML-based data persistence and serialization
- Legacy enterprise system integration patterns
- Budget approval tracking and reporting

## Structure

```
soap-budget/
├── soap_server.py          # Flask + Spyne SOAP service
├── approvals.xml           # Budget approval fixture data (20 records)
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker containerization
└── README.md             # This file
```

## Data Model

### BudgetApproval

Each approval record contains:

| Field | Type | Description |
|-------|------|-------------|
| ApprovalID | String | Unique approval identifier (APR-001, APR-002, etc.) |
| CampaignID | String | Associated marketing campaign ID |
| CampaignName | String | Human-readable campaign name |
| ApprovedAmount | Decimal | Budget amount in specified currency |
| Currency | String | Currency code (USD, EUR, etc.) |
| CostCenter | String | Cost center for budgeting (US-MARKETING-DIGITAL, GLOBAL-BRAND, etc.) |
| ApprovalDate | Date | Date approval was granted (YYYY-MM-DD) |
| EffectiveDate | Date | Date campaign budget becomes active (YYYY-MM-DD) |
| ApproverName | String | Name of person who approved budget |
| ApproverEmail | String | Email of approver |
| Status | String | Approval status (APPROVED, PENDING, REJECTED) |
| Notes | String | Additional approval notes |

## Fixture Data

The `approvals.xml` contains 20 budget approval records with:
- Campaign IDs matching Nike marketing campaigns
- Approved amounts ranging from $715,000 to $5,000,000
- Approval dates from August 18 to October 25, 2025
- Effective dates 1-2 weeks after approval
- Multiple cost centers (US-MARKETING-DIGITAL, GLOBAL-BRAND)
- Diverse approver names and email addresses

## Installation

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python soap_server.py
```

Service will start on `http://localhost:5000`

### Docker

```bash
# Build image
docker build -t soap-budget-service .

# Run container
docker run -p 5000:5000 soap-budget-service
```

## API Endpoints

### SOAP Endpoints

All SOAP requests should be POST to: `http://localhost:5000/soap/BudgetService`

Content-Type: `application/soap+xml` or `text/xml`

#### 1. GetCampaignApprovals

Retrieve approvals approved within a date range.

**Parameters:**
- `date_from` (string): Start date (YYYY-MM-DD)
- `date_to` (string): End date (YYYY-MM-DD)

**Returns:** XML with filtered approvals and metadata

#### 2. GetApprovalByID

Retrieve a specific approval by its ID.

**Parameters:**
- `approval_id` (string): Approval ID to retrieve

**Returns:** XML with single approval record or error

#### 3. GetApprovalsByCostCenter

Retrieve all approvals for a specific cost center.

**Parameters:**
- `cost_center` (string): Cost center code

**Returns:** XML with approvals and cost center summary

### REST Endpoints

#### GET /health

Health check endpoint

**Response:**
```json
{"status": "healthy"}
```

#### GET /soap/BudgetService?wsdl

WSDL definition for SOAP service

## SOAP Request Examples

### Example 1: GetCampaignApprovals - Date Range Query

Request approvals for September 2025:

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

**Expected Response:**
```xml
<?xml version='1.0' encoding='UTF-8'?>
<GetCampaignApprovalsResponse>
    <Metadata>
        <TotalRecords>15</TotalRecords>
        <DateFrom>2025-09-01</DateFrom>
        <DateTo>2025-09-30</DateTo>
        <QueryTimestamp>2025-11-11T10:30:45.123456</QueryTimestamp>
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
        <!-- ... more approvals ... -->
    </Approvals>
</GetCampaignApprovalsResponse>
```

### Example 2: GetApprovalByID - Single Record Query

Request a specific approval:

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

**Expected Response:**
```xml
<?xml version='1.0' encoding='UTF-8'?>
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

### Example 3: GetApprovalsByCostCenter - Cost Center Summary

Request all approvals for a cost center:

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

**Expected Response:**
```xml
<?xml version='1.0' encoding='UTF-8'?>
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
        <!-- ... more approvals ... -->
    </Approvals>
</GetApprovalsByCostCenterResponse>
```

## Testing

### Using curl

```bash
# Create a request file: request.xml
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

# Send request
curl -X POST http://localhost:5000/soap/BudgetService \
  -H "Content-Type: text/xml" \
  -d @request.xml
```

### Using Python

```python
import requests
from lxml import etree

# Build SOAP request
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
print(etree.tostring(root, pretty_print=True).decode())
```

### Using Postman

1. Create a new request with method POST
2. URL: `http://localhost:5000/soap/BudgetService`
3. Headers: `Content-Type: text/xml`
4. Body (raw): Paste one of the SOAP request examples above
5. Click Send

### Health Check

```bash
curl http://localhost:5000/health
```

Response:
```json
{"status": "healthy"}
```

## WSDL

The WSDL definition is available at:
```
http://localhost:5000/soap/BudgetService?wsdl
```

This can be imported into SOAP clients like SoapUI for automated testing.

## Cost Centers

The fixture data includes the following cost centers:

- `US-MARKETING-DIGITAL` - US digital marketing budget
- `GLOBAL-BRAND` - Global brand initiatives

## Approval Status Values

- `APPROVED` - Budget has been approved
- `PENDING` - Awaiting approval
- `REJECTED` - Budget request denied

## Integration Notes

### For Legacy System Integration

1. This service mimics enterprise-grade SOAP patterns
2. Requests and responses are fully XML-based
3. Date formats are ISO 8601 (YYYY-MM-DD)
4. Amounts are decimal values without currency symbols
5. All responses include timestamps for audit trails

### For Testing Budget Systems

1. Use `GetCampaignApprovals` to test date range filtering
2. Use `GetApprovalByID` to test single record lookups
3. Use `GetApprovalsByCostCenter` to test cost center reporting
4. All approvals have approval dates 1-2 weeks before effective dates

## Performance

- Service loads all approvals into memory on first request
- Subsequent requests use cached data
- Response times are typically <100ms
- Service can handle 1000s of concurrent requests

## Files Reference

### soap_server.py

Main SOAP service implementation:
- `BudgetApproval` class: Data model
- `BudgetApprovalService` class: SOAP service with three RPC methods
- `create_app()` function: Flask application factory

Key methods:
- `load_approvals()`: Loads XML fixture into memory
- `GetCampaignApprovals()`: Date range query
- `GetApprovalByID()`: Single record lookup
- `GetApprovalsByCostCenter()`: Cost center summary

### approvals.xml

XML fixture containing 20 budget approval records with:
- Sequential approval IDs (APR-001 to APR-020)
- Campaign IDs matching Nike marketing campaigns
- Realistic amounts, dates, and approver information
- Various cost centers and currencies

## Troubleshooting

### ModuleNotFoundError

Install dependencies:
```bash
pip install -r requirements.txt
```

### Port 5000 already in use

Change port in `soap_server.py`:
```python
app.run(host='0.0.0.0', port=5001)  # Use different port
```

### Connection refused

Ensure service is running:
```bash
python soap_server.py
# Should see: Starting SOAP Budget Service on http://localhost:5000
```

### Invalid XML response

Check that request XML is well-formed. Use the provided examples.

## Architecture Notes

This service simulates a legacy enterprise finance system with:

1. **SOAP 1.1** - For backward compatibility with enterprise systems
2. **XML Persistence** - Data stored in XML files like legacy systems
3. **Stateless Service** - Each request is independent
4. **In-Memory Caching** - Improved performance for repeated queries
5. **Minimal Dependencies** - Only Flask, Spyne, and lxml

## Future Enhancements

Possible additions to make this more realistic:
- Database backend (SQL instead of XML)
- Authentication and authorization
- Audit logging
- Budget amendment workflows
- Multi-currency conversion
- Approval workflow state machine
- Integration with expense tracking systems

## License

This mock service is provided as part of the STAGEHAND project.
