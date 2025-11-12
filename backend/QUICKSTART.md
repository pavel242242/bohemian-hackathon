# Quick Start Guide

## Installation

```bash
cd backend
npm install
```

## Start Development Server

```bash
npm run dev
```

You should see:
```
╔════════════════════════════════════════════╗
║  STAGEHAND Backend Server                  ║
║  Server running on http://localhost:4000   ║
║  Meta Mock at: http://localhost:3001       ║
║  Ready to query /api/campaigns             ║
╚════════════════════════════════════════════╝
```

## Test the Integration

### Quick Manual Test

```bash
# Test 1: Health check (should return {"status":"ok",...})
curl http://localhost:4000/health

# Test 2: Query campaigns (requires Meta mock on localhost:3001)
curl http://localhost:4000/api/campaigns

# Test 3: Query with parameters
curl "http://localhost:4000/api/campaigns?search=test&limit=5"
```

### Automated Test Suite

```bash
./test.sh
```

The test script will verify:
- Backend health
- Meta mock server connectivity
- Campaign queries with various parameters
- Error handling

## Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/campaigns` | GET | Query campaigns (recommended) |
| `/api/ads_archive` | GET | Direct proxy to Meta mock |

## Query Parameters for `/api/campaigns`

- `search` - Search term (optional)
- `limit` - Results per page (default: 10)
- `offset` - Pagination offset (default: 0)
- `after` - Pagination cursor (optional)

## Environment Variables

Create `.env` file (optional, defaults work):

```
PORT=4000
META_MOCK_SERVER=http://localhost:3001
NODE_ENV=development
```

## Response Format

All successful responses:
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-11-11T14:30:00.000Z"
}
```

All error responses:
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-11-11T14:30:00.000Z"
}
```

## Build for Production

```bash
npm run build    # Compiles TypeScript to dist/
npm start        # Runs compiled JavaScript
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 4000 in use | Set `PORT=4001 npm run dev` |
| Mock server unavailable | Ensure mock is running on port 3001 |
| TypeScript errors | Run `npm install` again |

## File Structure

```
backend/
├── src/
│   ├── server.ts       # Express server with endpoints
│   └── types.ts        # TypeScript interfaces
├── dist/               # Compiled JavaScript (after build)
├── package.json        # Dependencies & scripts
├── tsconfig.json       # TypeScript config
├── .env.example        # Environment variables template
└── README.md           # Full documentation
```

## Next Steps

1. Verify the backend starts: `npm run dev`
2. Test endpoints: `./test.sh`
3. Integrate with frontend
4. Add additional endpoints as needed
