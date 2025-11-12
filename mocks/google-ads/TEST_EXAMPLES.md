# Google Ads API Mock Server - Test Examples

This document contains example curl commands to test the Google Ads API mock server.

## Prerequisites

1. Start the server:
```bash
python server.py
```

The server will be available at `http://localhost:8000`

## Example Test Commands

### 1. Health Check
Check if the server is running and healthy.

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "google-ads-api-mock"
}
```

### 2. List All Campaigns
Get a list of all 7 Nike campaigns with their details.

```bash
curl http://localhost:8000/campaigns
```

**Expected Response:**
```json
{
  "campaigns": [
    {
      "id": "21843576928",
      "name": "Just Do It Marathon 2025",
      "status": "ENABLED",
      "budget_micros": 1500000000000,
      "channel": "YouTube",
      "start_date": "2025-09-11",
      "end_date": "2025-11-11",
      "metrics": {
        "impressions": 4250000,
        "clicks": 127500,
        "cost_micros": 1425000000000,
        "conversions": 5100,
        "conversion_value_micros": 2550000000000
      }
    }
    // ... 6 more campaigns
  ],
  "count": 7
}
```

### 3. Filter Campaigns by Status
Get only ENABLED campaigns.

```bash
curl "http://localhost:8000/campaigns?status=ENABLED"
```

Get only PAUSED campaigns.

```bash
curl "http://localhost:8000/campaigns?status=PAUSED"
```

### 4. Filter Campaigns by Channel
Get only YouTube campaigns.

```bash
curl "http://localhost:8000/campaigns?channel=YouTube"
```

Get only Search campaigns.

```bash
curl "http://localhost:8000/campaigns?channel=Search"
```

Get only Google Display campaigns.

```bash
curl "http://localhost:8000/campaigns?channel=Google%20Display"
```

### 5. Combined Filters
Get enabled YouTube campaigns.

```bash
curl "http://localhost:8000/campaigns?status=ENABLED&channel=YouTube"
```

### 6. Google Ads API - Search Endpoint (Non-Streaming)
Retrieve all campaigns in the search format (matching real Google Ads API).

```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search"
```

**Expected Response (partial):**
```json
{
  "results": [
    {
      "campaign": {
        "resourceName": "customers/1234567890/campaigns/21843576928",
        "id": "21843576928",
        "name": "Just Do It Marathon 2025",
        "status": "ENABLED",
        "biddingStrategyType": "TARGET_CPA",
        "budgetReferenceResourceName": "customers/1234567890/campaignBudgets/21843576928",
        "startDate": "20250911",
        "endDate": "20251111",
        "advertisingChannelType": "VIDEO"
      },
      "metrics": {
        "impressions": "4250000",
        "clicks": "127500",
        "costMicros": "1425000000000",
        "conversions": "5100.0",
        "conversionValueMicros": "2550000000000",
        "allConversionValueMicros": "2550000000000",
        "segments": {
          "date": "20251111"
        }
      },
      "campaignBudget": {
        "resourceName": "customers/1234567890/campaignBudgets/21843576928",
        "id": "21843576928",
        "amountMicros": "1500000000000"
      }
    }
    // ... more campaigns
  ],
  "fieldMask": "campaign.id,campaign.name,campaign.status,metrics.impressions,metrics.clicks,metrics.costMicros,campaignBudget.amountMicros",
  "totalResultsCount": "7",
  "requestId": "req_1234567890_search"
}
```

### 7. Google Ads API - Search with Date Filtering
Get campaigns active from October 1st onwards.

```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search?start_date=2025-10-01"
```

Get campaigns active between specific dates.

```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search?start_date=2025-10-01&end_date=2025-11-11"
```

### 8. Google Ads API - SearchStream Endpoint
Retrieve campaigns using the streaming endpoint (returns array of response objects).

```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:searchStream"
```

**Note:** This returns a JSON array where each element represents one campaign's data stream, mimicking the streaming nature of the real API.

**Expected Response Structure:**
```json
[
  {
    "results": [
      {
        "campaign": { ... },
        "metrics": { ... },
        "campaignBudget": { ... }
      }
    ],
    "fieldMask": "...",
    "requestId": "..."
  },
  // ... more campaign results
]
```

### 9. SearchStream with Date Range
Stream campaigns within a date range.

```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:searchStream?start_date=2025-09-01&end_date=2025-10-31"
```

### 10. Get All Fixture Data
View the raw fixture data to understand the data structure.

```bash
curl http://localhost:8000/fixtures
```

## Testing with jq (Optional)

If you have `jq` installed, you can parse and filter the responses:

### Get campaign names and budgets
```bash
curl -s http://localhost:8000/campaigns | jq '.campaigns[] | {name: .name, budget_micros: .budget_micros}'
```

### Get total impressions across all campaigns
```bash
curl -s http://localhost:8000/campaigns | jq '[.campaigns[].metrics.impressions] | add'
```

### Get campaigns with budget > $1M
```bash
curl -s http://localhost:8000/campaigns | jq '.campaigns[] | select(.budget_micros > 1000000000000)'
```

### Extract all metric names from a Google Ads API response
```bash
curl -s -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search" | jq '.results[0].metrics | keys'
```

## Testing with Python

```python
import requests
import json

# Health check
response = requests.get('http://localhost:8000/health')
print(json.dumps(response.json(), indent=2))

# Get campaigns
response = requests.get('http://localhost:8000/campaigns?channel=YouTube')
campaigns = response.json()
print(f"Found {campaigns['count']} YouTube campaigns")

# Google Ads API search
response = requests.post(
    'http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search',
    params={'start_date': '2025-10-01', 'end_date': '2025-11-11'}
)
data = response.json()
print(f"Found {data['totalResultsCount']} campaigns in date range")

# Check specific campaign
first_campaign = data['results'][0]
print(f"Campaign: {first_campaign['campaign']['name']}")
print(f"Impressions: {first_campaign['metrics']['impressions']}")
print(f"Clicks: {first_campaign['metrics']['clicks']}")
print(f"Cost: ${int(first_campaign['metrics']['costMicros']) / 1_000_000:.2f}")
```

## Testing with Different Customer IDs

The customer ID in the URL can be any value. The mock server will return the same data regardless:

```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/9876543210/googleAds:search"
curl -X POST "http://localhost:8000/googleads/v16/customers/YOUR_CUSTOMER_ID/googleAds:search"
```

## Response Format Notes

1. **Date Format**: Dates in the Google Ads API format are YYYYMMDD (e.g., 20251111)
2. **Money Format**: All monetary values are in micros (millionths of a dollar):
   - $1.00 = 1,000,000 micros
   - $700,000 = 700,000,000,000 micros
3. **Large Numbers**: Represented as strings in JSON to preserve precision
4. **camelCase**: All fields use camelCase (e.g., `costMicros`, `resourceName`)

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
PORT=3000 python server.py
```

### Invalid date error
```bash
# Date format must be YYYY-MM-DD
# This works:
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search?start_date=2025-10-01"

# This doesn't:
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search?start_date=10-01-2025"
```

### Empty results
If you get empty results, check:
1. The date range includes the campaign dates (Sept 11 - Nov 11, 2025)
2. You're using the correct channel name
3. The status is correctly specified (ENABLED vs PAUSED)
