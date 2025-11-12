# Google Ads API Mock Server

A FastAPI-based mock server for testing Google Ads API v16 integrations. Provides realistic campaign data with metrics matching the actual Google Ads API response structure.

## Features

- Mock implementation of Google Ads API v16 endpoints
- 7 realistic Nike campaigns with varied budgets and channels
- Support for date-based filtering
- Realistic API response format matching Google Ads API specifications
- Health check endpoint
- Easy Docker deployment

## Campaigns Included

The mock server includes 7 Nike campaigns:

1. **Just Do It Marathon 2025** - YouTube campaign ($1.5M budget)
2. **Nike Air Innovations** - Google Display campaign ($950K budget)
3. **Find Your Greatness Campaign** - Search campaign ($1.2M budget)
4. **Nike React Performance** - YouTube campaign, PAUSED ($700K budget)
5. **Unlimited Athlete Series** - Google Display campaign ($2M budget)
6. **Peak Performance Search** - Search campaign ($1.1M budget)
7. **Innovation Hub Digital** - YouTube campaign ($800K budget)

All campaigns have realistic metrics:
- Impressions: 1.85M - 5.6M
- Clicks: 55.5K - 228K
- Cost: Proportional to budget
- Conversions: Based on typical conversion rates

## Project Structure

```
google-ads/
├── server.py          # FastAPI application
├── fixtures.json      # Campaign fixture data
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md         # This file
```

## Quick Start

### Using Python

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

The server will start on `http://localhost:8000`

### Using Docker

1. Build the image:
```bash
docker build -t google-ads-mock:latest .
```

2. Run the container:
```bash
docker run -p 8000:8000 google-ads-mock:latest
```

## API Endpoints

### Health Check
```
GET /health
```

Returns server status.

### List Campaigns
```
GET /campaigns?status=ENABLED&channel=YouTube
```

Query parameters:
- `status`: Filter by status (ENABLED, PAUSED)
- `channel`: Filter by channel (YouTube, Google Display, Search)

### Search (Non-Streaming)
```
POST /googleads/v16/customers/{customer_id}/googleAds:search
```

Query parameters:
- `start_date`: Filter campaigns from this date (YYYY-MM-DD)
- `end_date`: Filter campaigns until this date (YYYY-MM-DD)

### Search Stream
```
POST /googleads/v16/customers/{customer_id}/googleAds:searchStream
```

Query parameters:
- `start_date`: Filter campaigns from this date (YYYY-MM-DD)
- `end_date`: Filter campaigns until this date (YYYY-MM-DD)

### Get All Fixtures
```
GET /fixtures
```

Returns the raw fixture data.

## Testing

### Get Health Status
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "google-ads-api-mock"
}
```

### List All Campaigns
```bash
curl http://localhost:8000/campaigns
```

### List Enabled YouTube Campaigns
```bash
curl "http://localhost:8000/campaigns?status=ENABLED&channel=YouTube"
```

### Search Campaigns (Non-Streaming)
```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search"
```

**Response:**
```json
{
  "results": [
    {
      "campaign": {
        "resourceName": "customers/1234567890/campaigns/21843576928",
        "id": "21843576928",
        "name": "Just Do It Marathon 2025",
        "status": "ENABLED",
        "advertisingChannelType": "VIDEO",
        "startDate": "20250911",
        "endDate": "20251111"
      },
      "metrics": {
        "impressions": "4250000",
        "clicks": "127500",
        "costMicros": "1425000000000",
        "conversions": "5100.0",
        "conversionValueMicros": "2550000000000"
      },
      "campaignBudget": {
        "resourceName": "customers/1234567890/campaignBudgets/21843576928",
        "id": "21843576928",
        "amountMicros": "1500000000000"
      }
    }
  ],
  "fieldMask": "campaign.id,campaign.name,campaign.status,metrics.impressions,metrics.clicks,metrics.costMicros,campaignBudget.amountMicros",
  "totalResultsCount": "7"
}
```

### Search Campaigns with Date Filter
```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search?start_date=2025-10-01&end_date=2025-11-11"
```

### Search Stream (Streaming Response)
```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:searchStream"
```

**Response:**
```json
[
  {
    "results": [
      {
        "campaign": {
          "resourceName": "customers/1234567890/campaigns/21843576928",
          "id": "21843576928",
          "name": "Just Do It Marathon 2025",
          "status": "ENABLED",
          "advertisingChannelType": "VIDEO"
        },
        "metrics": {
          "impressions": "4250000",
          "clicks": "127500",
          "costMicros": "1425000000000"
        }
      }
    ]
  }
]
```

## API Response Format

The mock server follows the Google Ads API v16 response format:

1. **camelCase Field Names**: All JSON fields use camelCase (e.g., `costMicros`, `resourceName`)
2. **String Numbers**: Large numbers (like cost in micros) are returned as strings to preserve precision
3. **Resource Names**: Follow the format `customers/{customerId}/resources/{id}`
4. **Metrics**: All metrics are included with realistic values
5. **Segments**: Date segments in YYYYMMDD format

## Fixture Data

The `fixtures.json` file contains the campaign data. Campaign budgets are specified in micros (millionths of a dollar):

- $700K = 700000000000 micros
- $2M = 2000000000000 micros

Metrics include:
- `impressions`: Total ad impressions
- `clicks`: Total clicks
- `cost_micros`: Total cost in micros
- `conversions`: Estimated conversions
- `conversion_value_micros`: Total conversion value in micros

## Customization

To add or modify campaigns:

1. Edit `fixtures.json` and add new campaign objects
2. Restart the server

To change the port:

```bash
PORT=3000 python server.py
```

Or with Docker:

```bash
docker run -p 3000:8000 -e PORT=8000 google-ads-mock:latest
```

## Real Google Ads API Reference

For more information about the actual Google Ads API v16:
- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [SearchStream Documentation](https://developers.google.com/google-ads/api/rest/common/search)
- [Campaign Resource Reference](https://developers.google.com/google-ads/api/fields/v16/campaign)

## Environment Variables

- `PORT`: Server port (default: 8000)
- `PYTHONUNBUFFERED`: Set to 1 for unbuffered output (default in Dockerfile)

## License

This is a mock server for testing purposes.
