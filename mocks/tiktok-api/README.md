# TikTok Ads API Mock Server

A mock Express.js server that simulates the TikTok Ads API (`business-api.tiktok.com/open_api/v1.3/`) for development and testing purposes.

## Overview

This mock server provides realistic Nike TikTok campaign data with authentic metrics for testing TikTok Ads integrations without consuming actual API credits or requiring authentication credentials.

### Features

- Mock TikTok Ads API endpoints with realistic response structures
- 5 pre-configured Nike campaign fixtures with authentic metrics
- Support for advertiser filtering and date range queries
- Matches official TikTok Ads API response format exactly
- Includes Docker support for containerized deployment
- Built with Express.js for simple, fast responses

## Quick Start

### Prerequisites

- Node.js 14+ (for local development)
- Docker (optional, for containerized deployment)

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

The server will start on `http://localhost:3001`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t tiktok-ads-mock:latest .
```

2. Run the container:
```bash
docker run -p 3001:3001 tiktok-ads-mock:latest
```

## API Endpoints

### Get All Campaigns

**Endpoint:** `GET /open_api/v1.3/campaign/get/`

Returns all campaigns with optional filtering.

**Query Parameters:**
- `advertiser_id` (optional): Filter campaigns by advertiser ID
- `start_date` (optional): Filter campaigns by start date (format: YYYY-MM-DD)
- `end_date` (optional): Filter campaigns by end date (format: YYYY-MM-DD)

**Example Request:**
```bash
curl "http://localhost:3001/open_api/v1.3/campaign/get/"
```

**Example Request with Filters:**
```bash
curl "http://localhost:3001/open_api/v1.3/campaign/get/?advertiser_id=1700000000000001&start_date=2024-09-01&end_date=2024-10-31"
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
        "campaign_type": "REACH",
        "objective": "REACH",
        "budget_mode": "TOTAL_BUDGET",
        "budget": "1500000",
        "budget_type": "DAILY",
        "status": "RUNNING",
        "channel": "TikTok",
        "create_time": 1725206400,
        "modify_time": 1730505600,
        "start_time": 1725206400,
        "end_time": 1732704000,
        "metrics": {
          "spend": "487250.50",
          "impressions": "45230000",
          "clicks": "892340",
          "conversions": "12450",
          "conversion_rate": "2.78",
          "cpc": "0.546",
          "cost_per_conversion": "39.15",
          "reach": "18900000",
          "frequency": "2.39"
        }
      }
    ]
  },
  "code": 0,
  "message": "OK",
  "request_id": "1730937600000000001"
}
```

### Get Specific Campaign

**Endpoint:** `GET /open_api/v1.3/campaign/get/:campaign_id`

Returns a specific campaign by ID.

**Path Parameters:**
- `campaign_id`: The campaign ID

**Query Parameters:**
- `advertiser_id` (optional): Verify campaign belongs to this advertiser

**Example Request:**
```bash
curl "http://localhost:3001/open_api/v1.3/campaign/get/1234567890123451"
```

**Response:**
```json
{
  "data": {
    "campaign": {
      "campaign_id": "1234567890123451",
      "campaign_name": "Spring Running Collection",
      "advertiser_id": "1700000000000001",
      ...
    }
  },
  "code": 0,
  "message": "OK",
  "request_id": "1730937600000000001"
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2025-11-11T12:00:00.000Z"
}
```

## Campaign Fixtures

The mock server includes 5 Nike TikTok campaigns with realistic data:

| Campaign Name | Budget | Status | Spend | Impressions | Conversions |
|---|---|---|---|---|---|
| Spring Running Collection | $1.5M | RUNNING | $487,250.50 | 45.2M | 12,450 |
| Air Max Hype | $850K | RUNNING | $678,920.75 | 38.4M | 18,920 |
| Jordan Legacy Campaign | $750K | RUNNING | $521,340.20 | 52.1M | 9,780 |
| Women's Sportswear Drop | $950K | RUNNING | $645,670.90 | 41.2M | 15,670 |
| Youth Basketball Series | $550K | PAUSED | $234,560.45 | 28.9M | 6,234 |

All campaigns are dated within the last 2 months from November 11, 2025.

## Response Format

All responses follow the official TikTok Ads API format:

```json
{
  "data": { ... },
  "code": 0,
  "message": "OK",
  "request_id": "unique_request_id"
}
```

### Response Codes

- `0`: Success
- `40001`: Campaign not found (404)
- `40004`: Endpoint not found (404)
- `50000`: Internal Server Error (500)

## Campaign Data Structure

Each campaign includes:

- **Basic Info**: `campaign_id`, `campaign_name`, `advertiser_id`, `channel`
- **Configuration**: `campaign_type`, `objective`, `budget`, `budget_mode`, `budget_type`
- **Status**: `status` (RUNNING/PAUSED)
- **Dates**: `create_time`, `modify_time`, `start_time`, `end_time` (Unix timestamps)
- **Metrics**:
  - `spend`: Total ad spend (in account currency)
  - `impressions`: Number of times ad was shown
  - `clicks`: Number of clicks on ad
  - `conversions`: Number of conversions
  - `conversion_rate`: Conversion percentage (%)
  - `cpc`: Cost per click
  - `cost_per_conversion`: Cost per conversion
  - `reach`: Number of unique users
  - `frequency`: Average frequency per user

## Testing with curl

### Test 1: Get all campaigns
```bash
curl http://localhost:3001/open_api/v1.3/campaign/get/
```

### Test 2: Get campaigns for specific advertiser
```bash
curl "http://localhost:3001/open_api/v1.3/campaign/get/?advertiser_id=1700000000000001"
```

### Test 3: Get campaigns within date range
```bash
curl "http://localhost:3001/open_api/v1.3/campaign/get/?start_date=2024-09-01&end_date=2024-11-11"
```

### Test 4: Get specific campaign
```bash
curl http://localhost:3001/open_api/v1.3/campaign/get/1234567890123451
```

### Test 5: Health check
```bash
curl http://localhost:3001/health
```

## File Structure

```
tiktok-api/
├── server.js           # Express server implementation
├── fixtures.json       # Campaign test data
├── package.json        # Node.js dependencies
├── Dockerfile          # Docker container configuration
└── README.md          # This file
```

## Environment Variables

- `PORT` (default: 3001): Port the server listens on

## Development

To modify the campaign data, edit `fixtures.json` and restart the server.

To add more endpoints, extend `server.js` following the same pattern as existing routes.

## API Reference

For the real TikTok Ads API documentation, visit:
- https://ads.tiktok.com/marketing_api/docs
- https://business-api.tiktok.com/portal

## License

MIT

## Notes

This is a mock server for development purposes only. It does not require authentication and returns static fixture data. For production use, integrate with the actual TikTok Ads API.
