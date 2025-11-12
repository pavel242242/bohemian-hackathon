# TikTok Ads API Mock Server - Testing Guide

## Quick Start

### 1. Start the Server Locally

```bash
cd /Users/chocho/projects/STAGEHAND/mocks/tiktok-api
npm install
npm start
```

Server will be available at `http://localhost:3001`

### 2. Test Examples with curl

#### Test 1: Get All Campaigns
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/"
```

**Response:**
```json
{
  "data": {
    "campaigns": [
      {
        "campaign_id": "1234567890123451",
        "campaign_name": "Spring Running Collection",
        "advertiser_id": "1700000000000001",
        "budget": "1500000",
        "status": "RUNNING",
        "metrics": {
          "spend": "487250.50",
          "impressions": "45230000",
          "clicks": "892340",
          "conversions": "12450"
        }
      }
      // ... more campaigns
    ]
  },
  "code": 0,
  "message": "OK",
  "request_id": "1730937600000000001"
}
```

#### Test 2: Get Specific Campaign
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/1234567890123451"
```

**Response:**
```json
{
  "data": {
    "campaign": {
      "campaign_id": "1234567890123451",
      "campaign_name": "Spring Running Collection",
      "advertiser_id": "1700000000000001",
      "status": "RUNNING",
      "budget": "1500000",
      "metrics": {
        "spend": "487250.50",
        "impressions": "45230000",
        "clicks": "892340",
        "conversions": "12450",
        "conversion_rate": "2.78",
        "cpc": "0.546",
        "cost_per_conversion": "39.15"
      }
    }
  },
  "code": 0,
  "message": "OK",
  "request_id": "1730937600000000002"
}
```

#### Test 3: Filter by Advertiser ID
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/?advertiser_id=1700000000000001"
```

Returns all 5 Nike campaigns for the specified advertiser.

#### Test 4: Filter by Date Range
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/?start_date=2024-09-01&end_date=2024-11-11"
```

Returns campaigns that overlap with the specified date range.

#### Test 5: Combined Filters
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/?advertiser_id=1700000000000001&start_date=2024-09-01&end_date=2024-11-11"
```

Returns Nike campaigns within the date range.

#### Test 6: Health Check
```bash
curl -X GET "http://localhost:3001/health"
```

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2025-11-11T22:52:10.045Z"
}
```

## Campaign IDs Reference

| Campaign Name | Campaign ID | Status | Budget |
|---|---|---|---|
| Spring Running Collection | 1234567890123451 | RUNNING | $1.5M |
| Air Max Hype | 1234567890123452 | RUNNING | $850K |
| Jordan Legacy Campaign | 1234567890123453 | RUNNING | $750K |
| Women's Sportswear Drop | 1234567890123454 | RUNNING | $950K |
| Youth Basketball Series | 1234567890123455 | PAUSED | $550K |

## Complete curl Example with jq Processing

To get formatted JSON output, pipe to `jq`:

```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/" | jq '.data.campaigns[] | {name: .campaign_name, spend: .metrics.spend, conversions: .metrics.conversions}'
```

**Output:**
```json
{
  "name": "Spring Running Collection",
  "spend": "487250.50",
  "conversions": "12450"
}
{
  "name": "Air Max Hype",
  "spend": "678920.75",
  "conversions": "18920"
}
// ... etc
```

## Docker Testing

### Build the Docker Image
```bash
cd /Users/chocho/projects/STAGEHAND/mocks/tiktok-api
docker build -t tiktok-ads-mock:latest .
```

### Run the Container
```bash
docker run -p 3001:3001 tiktok-ads-mock:latest
```

### Test from Container
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/"
```

## Integration Testing

### Test Response Structure
The mock API returns responses matching the TikTok Ads API format:

```bash
curl -s "http://localhost:3001/open_api/v1.3/campaign/get/" | \
  jq 'keys' # Should return: ["code", "data", "message", "request_id"]
```

### Test Response Codes
- **200**: Successful campaign retrieval
- **404**: Campaign not found (use invalid campaign ID)

Example for 404:
```bash
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/999999999999999"
```

**Response:**
```json
{
  "data": null,
  "code": 40001,
  "message": "Campaign not found",
  "request_id": "1730937600000000003"
}
```

## Performance Notes

- All responses are served from in-memory fixtures (sub-millisecond latency)
- No database calls or external API calls
- Suitable for development, testing, and continuous integration

## Troubleshooting

### Server won't start
```bash
# Check if port 3001 is already in use
lsof -i :3001

# Kill existing process if needed
kill -9 <PID>
```

### No response from curl
```bash
# Verify server is running
curl http://localhost:3001/health

# Check network connectivity
ping localhost
```

### Invalid JSON response
```bash
# Verify using jq
curl -X GET "http://localhost:3001/open_api/v1.3/campaign/get/" | jq empty
```

## File Locations

- Server code: `/Users/chocho/projects/STAGEHAND/mocks/tiktok-api/server.js`
- Campaign fixtures: `/Users/chocho/projects/STAGEHAND/mocks/tiktok-api/fixtures.json`
- Docker config: `/Users/chocho/projects/STAGEHAND/mocks/tiktok-api/Dockerfile`
- Full documentation: `/Users/chocho/projects/STAGEHAND/mocks/tiktok-api/README.md`
