# Google Ads API Mock Server - Project Summary

## What Was Created

A production-ready mock server for Google Ads API v16 with realistic Nike campaign data, built with FastAPI and Python. The server provides accurate response formatting matching Google's actual API specifications.

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| **server.py** | FastAPI application with endpoints | 259 |
| **fixtures.json** | 7 Nike campaigns with realistic data | 116 |
| **requirements.txt** | Python dependencies | 4 |
| **Dockerfile** | Docker container configuration | 20 |
| **README.md** | Complete documentation | 268 |
| **TEST_EXAMPLES.md** | Example curl commands & tests | 303 |
| **.dockerignore** | Docker build excludes | ~10 |

**Total Location:** `/Users/chocho/projects/STAGEHAND/mocks/google-ads/`

## 7 Nike Campaigns Included

1. **Just Do It Marathon 2025** (YouTube, $1.5M, ENABLED)
   - Impressions: 4.25M | Clicks: 127.5K | Cost: $1.425M

2. **Nike Air Innovations** (Google Display, $950K, ENABLED)
   - Impressions: 2.1M | Clicks: 63K | Cost: $875K

3. **Find Your Greatness Campaign** (Search, $1.2M, ENABLED)
   - Impressions: 3.8M | Clicks: 228K | Cost: $1.14M

4. **Nike React Performance** (YouTube, $700K, PAUSED)
   - Impressions: 1.85M | Clicks: 55.5K | Cost: $665K

5. **Unlimited Athlete Series** (Google Display, $2M, ENABLED)
   - Impressions: 5.6M | Clicks: 168K | Cost: $1.89M

6. **Peak Performance Search** (Search, $1.1M, ENABLED)
   - Impressions: 2.95M | Clicks: 177K | Cost: $1.045M

7. **Innovation Hub Digital** (YouTube, $800K, ENABLED)
   - Impressions: 2.2M | Clicks: 66K | Cost: $758K

## API Endpoints

### Core Google Ads API Endpoints
- `POST /googleads/v16/customers/{customerId}/googleAds:search`
- `POST /googleads/v16/customers/{customerId}/googleAds:searchStream`

### Convenience Endpoints
- `GET /health` - Server health check
- `GET /campaigns` - List campaigns with filters
- `GET /fixtures` - Raw fixture data
- `GET /` - API information

## Key Features

1. **Authentic API Format**
   - camelCase field names matching Google Ads API
   - resourceName format: `customers/{id}/campaigns/{id}`
   - Proper date formatting (YYYYMMDD)
   - Monetary values in micros (millionths of a dollar)

2. **Date Filtering**
   - Query parameters: `start_date` and `end_date` (YYYY-MM-DD)
   - Campaigns: Sept 11 - Nov 11, 2025

3. **Channel Support**
   - YouTube (VIDEO in API response)
   - Google Display (DISPLAY)
   - Search (SEARCH)

4. **Comprehensive Metrics**
   - Impressions
   - Clicks
   - Cost (in micros)
   - Conversions
   - Conversion value

5. **Deployment Ready**
   - Docker support with health check
   - Port configurable via environment variable
   - Production-grade error handling

## Running the Server

### Local Development
```bash
cd /Users/chocho/projects/STAGEHAND/mocks/google-ads
pip install -r requirements.txt
python server.py
```

### Docker
```bash
docker build -t google-ads-mock:latest .
docker run -p 8000:8000 google-ads-mock:latest
```

## Quick Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### List All Campaigns
```bash
curl http://localhost:8000/campaigns
```

### Google Ads API Search
```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search"
```

### Search with Date Filter
```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:search?start_date=2025-10-01&end_date=2025-11-11"
```

### SearchStream Endpoint
```bash
curl -X POST "http://localhost:8000/googleads/v16/customers/1234567890/googleAds:searchStream"
```

### Filter by Channel
```bash
curl "http://localhost:8000/campaigns?status=ENABLED&channel=YouTube"
```

## Example Response

The server returns responses in authentic Google Ads API format:

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
        "startDate": "20250911",
        "endDate": "20251111",
        "advertisingChannelType": "VIDEO"
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
        "amountMicros": "1500000000000"
      }
    }
  ],
  "totalResultsCount": "7"
}
```

## Technical Stack

- **Framework:** FastAPI 0.109.0
- **Server:** Uvicorn 0.27.0
- **Language:** Python 3.11
- **Data Format:** JSON fixtures
- **Containerization:** Docker

## Response Format Compliance

The server follows Google Ads API v16 specifications:

1. ✓ camelCase field names
2. ✓ String numbers for precision
3. ✓ Resource names in standard format
4. ✓ YYYYMMDD date format
5. ✓ Micros for monetary values
6. ✓ Proper HTTP status codes
7. ✓ Real metric relationships

## Use Cases

- Integration testing for Google Ads API clients
- Development of Google Ads data visualization tools
- Load testing API consumers
- Prototyping Google Ads features
- Training and documentation examples

## Documentation

- **README.md** - Complete setup and usage guide
- **TEST_EXAMPLES.md** - 10+ example curl commands with explanations
- **SUMMARY.md** - This file

## Next Steps

1. Run `python server.py` to start the mock server
2. Test endpoints using curl commands in TEST_EXAMPLES.md
3. Integrate with your Google Ads API client
4. Customize fixture data in fixtures.json as needed
5. Deploy with Docker if desired

## Notes

- Customer ID in URL can be any value (1234567890 or your actual ID)
- All campaigns have realistic metric relationships
- Budgets range from $700K to $2M
- No actual Google Ads API authentication required
- Mock server returns complete campaign data with all standard fields
