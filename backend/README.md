# STAGEHAND Backend

Minimal TypeScript + Express backend for querying the Meta Ad Library mock server.

## Setup

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
cd backend
npm install
```

### Configuration

Copy `.env.example` to `.env` (optional, defaults are already set):

```bash
cp .env.example .env
```

Default configuration:
- `PORT=4000` - Backend server port
- `META_MOCK_SERVER=http://localhost:3001` - Meta mock server URL

## Running the Server

### Development Mode (with hot-reload via ts-node)

```bash
npm run dev
```

The server will start on `http://localhost:4000`

### Production Build

```bash
npm run build
npm start
```

## API Endpoints

### Health Check
```bash
GET /health
```

Returns:
```json
{
  "status": "ok",
  "timestamp": "2025-11-11T14:30:00.000Z"
}
```

### Query Campaigns (Recommended)
```bash
GET /api/campaigns
```

Query Parameters:
- `search` (optional) - Search term
- `limit` (optional, default: 10) - Number of results
- `offset` (optional, default: 0) - Offset for pagination
- `after` (optional) - Pagination cursor

Example:
```bash
curl "http://localhost:4000/api/campaigns?search=test&limit=5"
```

Response:
```json
{
  "success": true,
  "data": {
    "data": [...],
    "paging": {...}
  },
  "timestamp": "2025-11-11T14:30:00.000Z"
}
```

### Direct Ads Archive Query
```bash
GET /api/ads_archive
```

Direct proxy to the Meta mock server's `/ads_archive` endpoint. Pass through any parameters supported by the mock server.

Example:
```bash
curl "http://localhost:4000/api/ads_archive?search=campaign"
```

## Testing the Integration

### Prerequisites
1. Make sure the Meta Ad Library mock server is running on `http://localhost:3001`
2. The backend should be running on `http://localhost:4000`

### Quick Test Script

```bash
# Test 1: Health check
curl http://localhost:4000/health

# Test 2: Query campaigns without parameters
curl http://localhost:4000/api/campaigns

# Test 3: Query campaigns with search
curl "http://localhost:4000/api/campaigns?search=test"

# Test 4: Query with limit
curl "http://localhost:4000/api/campaigns?limit=20"

# Test 5: Direct ads archive query
curl http://localhost:4000/api/ads_archive
```

### Expected Output Example

A successful request should return:
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": "123",
        "name": "Campaign Name",
        "advertiser_name": "Company Name",
        ...
      }
    ],
    "paging": {
      "cursor": "...",
      "after": "..."
    }
  },
  "timestamp": "2025-11-11T14:30:00.000Z"
}
```

If the mock server is not running, you'll get:
```json
{
  "success": false,
  "error": "connect ECONNREFUSED 127.0.0.1:3001",
  "timestamp": "2025-11-11T14:30:00.000Z"
}
```

## Project Structure

```
backend/
├── src/
│   ├── server.ts       # Express server & endpoints
│   └── types.ts        # TypeScript interfaces
├── package.json        # Dependencies & scripts
├── tsconfig.json       # TypeScript configuration
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md          # This file
```

## Key Features

- CORS enabled for frontend integration
- TypeScript for type safety
- Proper error handling with consistent response format
- Logging for debugging
- Two query endpoints (recommended and direct proxy)
- Environment variable configuration
- Hot-reload development mode

## File Descriptions

### server.ts
Main Express application with:
- CORS middleware setup
- Health check endpoint
- `/api/campaigns` - Main endpoint for querying with query parameters
- `/api/ads_archive` - Direct proxy to mock server
- Error handling and 404 handler
- Server startup with status banner

### types.ts
TypeScript interfaces for:
- `AdArchiveAd` - Individual ad object structure
- `AdArchiveResponse` - Meta mock server response format
- `ApiResponse<T>` - Consistent API response wrapper
- `CampaignQueryParams` - Query parameter types

## Troubleshooting

### Port 4000 Already in Use
```bash
# Use a different port
PORT=4001 npm run dev
```

### Cannot Connect to Meta Mock Server
- Ensure mock server is running: `http://localhost:3001`
- Check `META_MOCK_SERVER` in `.env`
- Verify network connectivity

### TypeScript Compilation Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. Start the backend: `npm run dev`
2. Test endpoints with curl or Postman
3. Integrate with frontend
4. Extend with additional endpoints as needed
