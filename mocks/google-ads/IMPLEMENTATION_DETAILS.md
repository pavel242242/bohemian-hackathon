# Google Ads API Mock Server - Implementation Details

## Project Overview

A production-ready FastAPI-based mock server that accurately emulates Google Ads API v16 responses with realistic Nike campaign data.

**Location:** `/Users/chocho/projects/STAGEHAND/mocks/google-ads/`

## Files Created

### Core Files

1. **server.py** (259 lines)
   - FastAPI application entry point
   - 6 main endpoints + root endpoint
   - Date filtering logic with validation
   - Google Ads API response formatting
   - Error handling with proper HTTP status codes

2. **fixtures.json** (116 lines)
   - 7 Nike campaigns with realistic data
   - Campaign IDs, names, budgets, channels
   - Date ranges (Sept 11 - Nov 11, 2025)
   - Complete metrics (impressions, clicks, cost, conversions)
   - JSON-formatted for easy modification

3. **requirements.txt** (4 lines)
   - fastapi==0.109.0
   - uvicorn[standard]==0.27.0
   - python-multipart==0.0.6
   - pydantic==2.5.3

4. **Dockerfile** (20 lines)
   - Python 3.11 base image
   - Dependency installation
   - Health check configuration
   - Port exposure (8000)
   - Production-ready setup

### Documentation Files

5. **README.md** (268 lines)
   - Complete setup instructions
   - API endpoint documentation
   - Example curl commands
   - Response format explanations
   - Environment variables guide

6. **TEST_EXAMPLES.md** (303 lines)
   - 10+ detailed test examples
   - curl commands with explanations
   - Expected responses shown in full
   - Python testing examples
   - jq filtering examples
   - Troubleshooting guide

7. **SUMMARY.md** (5.9K)
   - Executive overview
   - Feature highlights
   - Quick start commands
   - Use cases
   - Technical stack

8. **QUICK_START.sh** (Executable bash script)
   - Automated test runner
   - Server connectivity check
   - Multiple test examples
   - User-friendly output

9. **IMPLEMENTATION_DETAILS.md** (This file)
   - Technical architecture
   - Code structure explanation
   - API design decisions

### Support Files

10. **.dockerignore** (91 bytes)
    - Docker build optimization
    - Excludes unnecessary files

## Implementation Architecture

### API Endpoints

#### 1. Health Check
```
GET /health
```
- Returns: `{"status": "healthy", "service": "google-ads-api-mock"}`
- Purpose: Server health verification

#### 2. List Campaigns (Convenience)
```
GET /campaigns
Query params: status, channel
```
- Returns: Array of campaign objects with raw fixture data
- Filters: Can filter by status (ENABLED/PAUSED) and channel (YouTube/Google Display/Search)

#### 3. Google Ads API Search (Non-Streaming)
```
POST /googleads/v16/customers/{customerId}/googleAds:search
Query params: start_date, end_date
```
- Returns: Single response with results array
- Format: Matches real Google Ads API response structure
- Filtering: Date range filtering supported

#### 4. Google Ads API SearchStream
```
POST /googleads/v16/customers/{customerId}/googleAds:searchStream
Query params: start_date, end_date
```
- Returns: Array of response objects (one per campaign)
- Format: Mimics streaming nature of real API
- Filtering: Date range filtering supported

#### 5. Get Fixtures
```
GET /fixtures
```
- Returns: Raw fixture data for debugging/reference

#### 6. Root Endpoint
```
GET /
```
- Returns: API information and available endpoints

### Key Implementation Features

#### Response Format Compliance

The server matches Google Ads API v16 format:

```json
{
  "campaign": {
    "resourceName": "customers/{id}/campaigns/{id}",
    "id": "...",
    "name": "...",
    "status": "ENABLED|PAUSED",
    "biddingStrategyType": "TARGET_CPA",
    "startDate": "YYYYMMDD",
    "endDate": "YYYYMMDD",
    "advertisingChannelType": "VIDEO|DISPLAY|SEARCH"
  },
  "metrics": {
    "impressions": "string",
    "clicks": "string",
    "costMicros": "string",
    "conversions": "string",
    "conversionValueMicros": "string"
  },
  "campaignBudget": {
    "resourceName": "customers/{id}/campaignBudgets/{id}",
    "amountMicros": "string"
  }
}
```

#### Field Name Conventions

- camelCase (not snake_case) - matches Google Ads API
- Numbers as strings for precision preservation
- Monetary values in micros (1/1,000,000 of a dollar)
- Dates in YYYYMMDD format (no hyphens)

#### Date Filtering Logic

```python
def filter_campaigns_by_date(campaigns, start_date=None, end_date=None):
    # Filters campaigns where:
    # - campaign.end_date >= start_date (if start_date provided)
    # - campaign.start_date <= end_date (if end_date provided)
    # - Handles YYYY-MM-DD format input
    # - Converts to datetime for comparison
```

#### Campaign Metadata

Each campaign includes:
- ID: Unique identifier
- Name: Realistic Nike campaign name
- Status: ENABLED or PAUSED
- Budget: $700K - $2M range
- Channel: YouTube, Google Display, or Search
- Start/End dates: Sept 11 - Nov 11, 2025
- Metrics: Realistic values with proper relationships

### Campaign Data Details

| Campaign | Budget | Channel | Status | Impressions | Clicks |
|----------|--------|---------|--------|-------------|--------|
| Just Do It Marathon 2025 | $1.5M | YouTube | ENABLED | 4.25M | 127.5K |
| Nike Air Innovations | $950K | Display | ENABLED | 2.1M | 63K |
| Find Your Greatness | $1.2M | Search | ENABLED | 3.8M | 228K |
| Nike React Performance | $700K | YouTube | PAUSED | 1.85M | 55.5K |
| Unlimited Athlete Series | $2M | Display | ENABLED | 5.6M | 168K |
| Peak Performance Search | $1.1M | Search | ENABLED | 2.95M | 177K |
| Innovation Hub Digital | $800K | YouTube | ENABLED | 2.2M | 66K |

### Monetization Format

All monetary values use "micros" convention:
- $1 = 1,000,000 micros
- $700,000 = 700,000,000,000 micros

Large numbers stored as strings to preserve precision in JSON.

## Code Structure

### server.py Structure

```
1. Imports (FastAPI, Uvicorn, JSON, Path)
2. Configuration (Load fixtures from JSON)
3. Helper Functions:
   - parse_date_string()
   - format_date_string()
   - build_google_ads_row()
   - filter_campaigns_by_date()
4. FastAPI App Initialization
5. Endpoints:
   - GET /health
   - POST /googleads/v16/customers/{id}/googleAds:searchStream
   - POST /googleads/v16/customers/{id}/googleAds:search
   - GET /campaigns
   - GET /fixtures
   - GET /
6. Main Entry Point
```

### Key Functions

#### `build_google_ads_row(campaign, custom_date=None)`
Transforms fixture campaign data into Google Ads API format:
- Maps channel names to API values (YouTube→VIDEO, etc.)
- Formats dates (20250911 format)
- Converts numbers to strings
- Builds resourceName strings
- Includes all required fields

#### `filter_campaigns_by_date(campaigns, start_date=None, end_date=None)`
Filters campaigns by date range:
- Parses YYYY-MM-DD input
- Compares campaign.start_date and campaign.end_date
- Handles None values gracefully
- Raises ValueError for invalid dates

### Error Handling

- HTTPException for invalid dates (400 status)
- Proper error messages with details
- Graceful handling of missing filters

## Deployment Options

### Local Development
```bash
cd /Users/chocho/projects/STAGEHAND/mocks/google-ads
pip install -r requirements.txt
python server.py
```

### Docker Deployment
```bash
docker build -t google-ads-mock:latest .
docker run -p 8000:8000 google-ads-mock:latest
```

### Custom Port
```bash
PORT=3000 python server.py
```

## Testing Verification

The mock server was tested with:

1. Health check endpoint
2. Campaign listing
3. Google Ads API search endpoint
4. Date filtering functionality
5. Channel filtering
6. Status filtering
7. JSON response format validation

All endpoints return properly formatted responses matching Google Ads API specifications.

## Performance Characteristics

- In-memory data loading (fast startup)
- No database dependencies
- Lightweight JSON parsing
- Fast response times
- Suitable for testing/development

## Extensibility

### Adding More Campaigns
Edit `fixtures.json` and add campaign objects to the campaigns array.

### Modifying Response Format
Update `build_google_ads_row()` function to add/remove fields.

### Adding New Endpoints
Add new route functions with @app.get() or @app.post() decorators.

### Changing Port
Use PORT environment variable or modify uvicorn.run() call.

## API Compatibility

The server is compatible with:
- Google Ads API client libraries
- Direct HTTP clients
- curl/Postman
- Python requests
- JavaScript fetch
- Any HTTP tool

No special authentication required for mock server.

## Data Quality

Campaign metrics maintain realistic relationships:
- CTR (Click-Through Rate): 2-8% range
- Conversion Rate: ~2-3% of clicks
- Cost Per Click: Varies by channel
- ROAS: Positive conversion value vs. cost

All data is synthetic but follows advertising industry norms.
