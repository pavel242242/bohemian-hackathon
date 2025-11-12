# Nike Campaigns Intelligence System

## What We Built

24-hour hackathon MVP with groundbreaking **autonomous driver generation** for multi-source campaign data aggregation.

STAGEHAND is an intelligent system that understands natural language questions about Nike advertising campaigns across multiple platforms and automatically extracts, unifies, and analyzes data from complex APIs—without hand-coding individual integrations.

## The Problem

Marketing teams need to query campaign data from multiple advertising sources:
- **Meta** (Facebook/Instagram Ad Library)
- **Google Ads** (YouTube, Display, Search)
- **TikTok Ads** (TikTok business platform)
- **Seznam Ads** (Czech search engine with complex nested pagination)
- **SOAP Budgets** (Internal enterprise finance approval system)

Each API has **completely different**:
- Authentication methods (API keys, OAuth, XML headers)
- Pagination patterns (cursor-based, offset-based, nested)
- Response formats (JSON wrapped, deeply nested, XML)
- Rate limiting strategies
- Data structure and field naming

**Traditional approach:** Hire engineers to spend days hand-coding each integration.

**Our approach:** One intelligent agent that figures it out automatically.

## The Solution

An AI-powered agent that:

1. **Understands natural language queries** - "Show me top 10 Meta campaigns with budget > $50k"
2. **Checks data freshness** - Knows when to query cache vs. refresh
3. **Automatically generates data extraction drivers** - Builds Python code for new APIs on-the-fly
4. **Orchestrates multi-source extraction** - Extracts from all sources simultaneously
5. **Unifies and analyzes** - Aggregates to DuckDB, runs SQL queries
6. **Answers intelligently** - Returns results with context about sources and freshness

## Key Innovation: Autonomous Driver Generation

When a user asks for data from a previously unknown API source:

### The Four-Step Process

```
User Query: "Show me Seznam campaigns"
      ↓
Agent: "No driver exists for Seznam. Building one..."
      ↓
Step 1: API EXPLORER
├─ Calls /api/v2/campaigns endpoint
├─ Detects cursor-based pagination in response
├─ Analyzes nested response structure
├─ Identifies authentication headers needed
└─ Maps field types and data nesting
      ↓
Step 2: SOURCE GENERATOR
├─ Generates Python dlthub connector code
├─ Creates seznam_ads.py with pagination logic
├─ Adds response unwrapping for nested data
├─ Implements error handling and retries
└─ Returns generated source file
      ↓
Step 3: DRIVER MANAGER
├─ Tests generated code against real API
├─ Catches errors (auth, parsing, pagination)
├─ Analyzes failures and suggests fixes
├─ Refines code iteratively (up to 3 attempts)
└─ Validates data extraction works
      ↓
Step 4: PIPELINE EXECUTION
├─ Loads driver into dlthub pipeline
├─ Extracts campaign data
├─ Normalizes schema to unified format
├─ Writes to DuckDB tables
└─ Agent queries results
      ↓
Response: 237 Seznam campaigns extracted and aggregated
```

### Component Details

**API Explorer** (`api_explorer.py`)
- Discovers pagination patterns (cursor, offset, page-based)
- Identifies authentication requirements
- Maps response structure and nested fields
- Detects rate limiting headers
- Analyzes field types and data wrapping

**Source Generator** (`source_generator.py`)
- Creates Python dlthub connector code
- Generates pagination loops based on discovered patterns
- Handles authentication headers
- Unwraps nested responses
- Normalizes field names to unified schema
- Includes error handling

**Driver Manager** (`driver_manager.py`)
- Tests generated source against API
- Parses error messages from failed runs
- Analyzes stack traces and API responses
- Refines code iteratively (self-healing)
- Validates extracted data format
- Persists working drivers for reuse

**Intelligence Agent** (`agent.py`)
- Parses natural language queries
- Determines which data sources to query
- Builds drivers for unknown sources
- Orchestrates parallel extraction
- Checks data freshness
- Queries DuckDB for results
- Formats and returns answers

## Architecture Highlights

### Data Layer
- **Mock API Servers** - Express.js, Node.js simulating realistic complex advertising APIs
- **dlthub Pipelines** - Professional Python data extraction with field mapping and merge strategies
- **DuckDB** - Fast in-process SQL analytics database for aggregated campaign data
- **Driver Repository** - Generated Python sources stored and reused

### Backend
- **Express.js** - REST API for query submission and results retrieval
- **TypeScript** - Type-safe API definitions and request handling
- **Query Engine** - Submits questions to intelligent agent, streams responses

### Frontend
- **Svelte** - Component-based reactive UI
- **Vite** - Fast build tool
- **Query Interface** - Natural language input form with results table
- **Real-time Logs** - Shows agent activity and driver generation progress

### Mocks (For Demo)
- **Meta Ad Library Mock** (port 3001) - Express.js, Facebook/Instagram API structure
- **Google Ads Mock** (port 8000) - Realistic Google Ads API responses
- **TikTok Ads Mock** (port 3003) - TikTok business API structure
- **Seznam Ads Mock** (port 3004) - Complex nested pagination example
- **SOAP Budget Mock** (port 5001) - XML enterprise finance system

## Demo Data Sources

### 1. Meta Ad Library (8 campaigns)
```
Air Max Day - $2.5M budget
Nike By You - $1.2M budget
Women's Basketball - $1.1M budget
Run with Pegasus - $850K budget
Fall Collection - $1.5M budget
Just Do It - $1.8M budget
Retro Sneaker - $780K budget
Training Club - $1.15M budget
```

### 2. Google Ads (7 campaigns)
```
Just Do It Marathon - $1.5M budget (YouTube)
Air Innovations - $950K budget (Display)
Find Your Greatness - $1.2M budget (Search)
React Performance - $700K budget (YouTube)
Unlimited Athlete - $2M budget (Display)
Peak Performance - $1.1M budget (Search)
Innovation Hub - $800K budget (YouTube)
```

### 3. TikTok Ads (5 campaigns)
```
Spring Running Collection - $1.5M budget
Air Max Hype - $850K budget
Jordan Legacy - $750K budget
Women's Sportswear - $950K budget
Youth Basketball - $550K budget
```

### 4. Seznam Ads (Complex Example - Shows Driver Generation)
- Complex nested pagination structure
- Custom authentication headers
- Demonstrates autonomous driver building capability

### 5. SOAP Budgets (20 approval records)
- Cross-references all campaigns above
- Approval dates and status
- Cost center tracking
- Approver information

## Technical Stack

### Data Processing
- **Python 3.x** - dlthub sources, agent logic
- **dlthub** - Professional ETL framework for connector development
- **DuckDB** - SQL analytics engine with native Python bindings
- **Requests** - HTTP client for API exploration

### Backend
- **Node.js** - Runtime
- **TypeScript** - Type-safe API development
- **Express** - Web framework
- **CORS** - Cross-origin handling for frontend

### Frontend
- **SvelteKit** - Modern reactive framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Fetch API** - HTTP client

### Infrastructure
- **Express.js** - Mock API servers (multiple instances)
- **Shell Scripts** - Orchestration and startup
- **File System** - DuckDB persistence

## What Makes This Special

### The Traditional Way
```
Marketing team requests data from new source
  ↓
Schedule meeting with engineering team
  ↓
Write API specification document
  ↓
Allocate developer (3-5 days)
  ↓
Development:
  - Read API docs
  - Build authentication
  - Handle pagination
  - Map response to schema
  - Add error handling
  - Test with real data
  ↓
Code review, fixes, deployment
  ↓
RESULT: 1 API integrated after 5+ days
```

### The STAGEHAND Way
```
Marketing team asks agent: "Show me Seznam campaigns"
  ↓
Agent detects: No existing driver
  ↓
API Explorer automatically:
  - Discovers pagination pattern
  - Detects authentication
  - Maps response structure
  ↓
Source Generator creates connector code
  ↓
Driver Manager tests and refines (self-healing)
  ↓
Data flows into DuckDB
  ↓
RESULT: New API integrated in minutes, no coding required
```

### Key Advantages
- **Speed** - Add new sources in minutes, not days
- **Flexibility** - Adapts to different API patterns automatically
- **Self-Healing** - Iteratively refines code when errors occur
- **Knowledge Reuse** - Generated drivers are stored and reused
- **Scalable** - Build multiple drivers in parallel
- **Low Maintenance** - No custom integrations to update when APIs change

## Example Workflow

### Query Submission
```
User: "Show me Nike campaigns with budget > $100K, sorted by spend"

Agent receives query and:
1. Parses natural language → extract intent
2. Checks DuckDB → is data fresh?
3. If fresh → runs SQL query
4. If stale → triggers data refresh
5. If new source → builds driver autonomously
```

### Multi-Source Extraction
```
Agent executing: Extract all campaign sources
├─ Meta Ad Library → 8 campaigns extracted
├─ Google Ads → 7 campaigns extracted
├─ TikTok Ads → 5 campaigns extracted
├─ Seznam Ads → [Building driver...] → Campaigns extracted
└─ SOAP Budgets → 20 approval records extracted

All data normalized to unified schema
Loaded into DuckDB
Ready for querying
```

### Result Formatting
```
Query: "Top 10 campaigns by budget"

Results Table:
┌─────────────┬──────────┬───────────┬──────────┐
│ Campaign    │ Source   │ Channel   │ Budget   │
├─────────────┼──────────┼───────────┼──────────┤
│ Unlimited   │ Google   │ Display   │ $2.0M    │
│ Spring Run  │ TikTok   │ TikTok    │ $1.5M    │
│ Just Do It  │ Google   │ YouTube   │ $1.5M    │
└─────────────┴──────────┴───────────┴──────────┘

Metadata:
Sources: Google, TikTok, Meta
Last refreshed: 2 minutes ago
Driver versions: meta@v1, google@v1, tiktok@v1
```

## File Structure

```
STAGEHAND/
├── mocks/                          # Simulated advertising APIs
│   ├── meta-api/                   # Meta Ad Library mock (port 3001)
│   │   ├── package.json
│   │   ├── server.js
│   │   └── fixtures.json
│   ├── google-ads/                 # Google Ads mock (port 8000)
│   │   └── ...
│   ├── tiktok-api/                 # TikTok Ads mock (port 3003)
│   │   └── ...
│   ├── seznam-ads/                 # Seznam Ads mock (port 3004)
│   │   └── ...
│   └── soap-budget/                # Budget approval mock (port 5001)
│       └── ...
│
├── pipelines/                      # Core intelligence system
│   ├── agent.py                    # Main orchestration agent
│   ├── api_explorer.py             # Autonomous API discovery
│   ├── source_generator.py         # Generates dlthub connectors
│   ├── driver_manager.py           # Iterative code refinement
│   ├── source_templates.py         # Code generation templates
│   ├── nike_campaigns_pipeline.py  # Main dlthub pipeline
│   ├── query.py                    # CLI query interface
│   ├── sources/                    # Generated driver storage
│   │   ├── meta_ads.py
│   │   ├── google_ads.py
│   │   ├── tiktok_ads.py
│   │   └── seznam_ads.py
│   ├── nike_campaigns.duckdb       # Aggregated data store
│   └── venv/                       # Python virtual environment
│
├── backend/                        # Express REST API
│   ├── src/
│   │   ├── server.ts              # Express app
│   │   ├── api.ts                 # API routes
│   │   └── types.ts               # TypeScript definitions
│   ├── package.json
│   └── tsconfig.json
│
├── ui/                             # Svelte frontend
│   ├── src/
│   │   ├── routes/
│   │   │   └── +page.svelte       # Query interface
│   │   ├── lib/
│   │   │   └── api.ts             # Backend client
│   │   ├── app.svelte
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
│
├── logs/                           # Server output logs
│   ├── meta-mock.log
│   ├── google-mock.log
│   ├── tiktok-mock.log
│   ├── seznam-mock.log
│   └── soap-mock.log
│
├── start-all-mocks.sh             # Launch all mock servers
├── stop-all-mocks.sh              # Stop all servers
├── test-all-mocks.sh              # Verify mock functionality
├── plan.md                         # Implementation planning doc
├── STATUS.md                       # Current status tracker
├── QUICKSTART.md                   # Quick start guide
└── OVERVIEW.md                     # This file
```

## Getting Started

### Prerequisites
- Node.js 16+ (for mocks, backend, UI)
- Python 3.8+ (for data extraction)
- npm or yarn

### Quick Start

1. **Start all mock servers:**
```bash
cd /Users/chocho/projects/STAGEHAND
./start-all-mocks.sh
```

2. **Test mock connectivity:**
```bash
./test-all-mocks.sh
```

3. **Query data (Python CLI):**
```bash
cd pipelines
source venv/bin/activate
python query.py "Show me top 10 Nike campaigns"
```

4. **Start backend (optional):**
```bash
cd backend
npm install
npm run dev
# Backend on http://localhost:4000
```

5. **Start frontend (optional):**
```bash
cd ui
npm install
npm run dev
# Frontend on http://localhost:5173
```

### Example Queries

**Top campaigns:**
```
"Show me the top 20 Nike campaigns"
"What are the highest budget campaigns?"
"Which campaigns have the most impressions?"
```

**By source/channel:**
```
"Show me Meta campaigns"
"What campaigns are running on Google?"
"Which platforms have active Nike ads?"
```

**By metrics:**
```
"Show campaigns with budget > $1M"
"What are recent campaigns (last week)?"
"Show campaigns by channel"
```

**Aggregated insights:**
```
"What's the total Nike advertising spend?"
"Which channel has the most campaigns?"
"Show budget distribution by source"
```

## How It Works: Step-by-Step Example

### Scenario: User Asks About Unknown Source

**Input:**
```
User: "Show me Seznam campaigns from the last month"
```

**Agent Processing:**

1. **Query Parsing**
   - Intent: Retrieve campaigns
   - Source: Seznam (new/unknown)
   - Filter: Last month date range

2. **Driver Check**
   - Check: sources/seznam_ads.py exists?
   - Result: No existing driver found

3. **Build Driver**
   - API Explorer discovers:
     - Base URL: http://localhost:3004
     - Endpoint: /api/v2/campaigns
     - Auth: X-Seznam-Api-Key header
     - Pagination: Cursor-based (next_cursor in response)
     - Response: { data: [...], pagination: { next_cursor } }

   - Source Generator creates seznam_ads.py:
     ```python
     @dlt.resource
     def seznam_campaigns():
         url = "http://localhost:3004/api/v2/campaigns"
         cursor = None
         while True:
             params = {"cursor": cursor} if cursor else {}
             headers = {"X-Seznam-Api-Key": "demo_api_key"}
             response = requests.get(url, params=params, headers=headers)
             data = response.json()
             yield from data["data"]
             cursor = data.get("pagination", {}).get("next_cursor")
             if not cursor:
                 break
     ```

   - Driver Manager tests:
     - Run: python seznam_ads.py
     - Result: ✓ 237 campaigns extracted
     - Validation: ✓ All required fields present

4. **Extract Data**
   - Load seznam_ads.py into pipeline
   - Execute extraction
   - Transform to unified schema
   - Write to DuckDB

5. **Query Results**
   - SQL: SELECT * FROM seznam_campaigns WHERE date > last_month
   - Result: 47 campaigns from last month

6. **Return to User**
   ```
   Found 47 Seznam campaigns from last month:
   - Most recent: 2 days ago
   - Budget range: $250K - $1.8M
   - Total spend: $18.2M
   ```

## Innovation Highlights

### Autonomous Pagination Discovery
- Detects cursor-based pagination
- Detects offset/limit pagination
- Detects page-number pagination
- Handles one-off pages
- Respects rate limiting

### Smart Response Parsing
- Unwraps nested JSON structures
- Maps different field naming conventions
- Converts data types appropriately
- Handles optional fields gracefully
- Validates required fields

### Iterative Refinement
- Tests generated code immediately
- Analyzes error messages
- Adjusts pagination logic
- Fixes authentication headers
- Retries up to 3 times

### Unified Schema
- All sources → Standardized campaign schema
- Consistent field names across platforms
- Normalized budget and spend values
- Unified date/time formats
- Source attribution maintained

## Real-World Impact

### For Marketing Teams
- **Self-service data access** - Ask questions, get answers
- **No dependencies** - Don't wait for engineering
- **Fresh data** - Automatic refreshes
- **Multi-source insights** - See all platforms at once

### For Engineering Teams
- **Less maintenance** - Generated drivers self-heal
- **Faster integration** - Minutes instead of days
- **Scalability** - Add 10 sources as easily as 1
- **Knowledge capture** - Patterns are discovered and reused

### For Organizations
- **Cost savings** - Less custom development
- **Time savings** - Faster data access
- **Flexibility** - Easy to add new sources
- **Reliability** - Automated testing and refinement

## Performance Characteristics

- **Query speed** - Sub-second SQL queries on DuckDB
- **Extraction time** - 10-30 seconds per source (parallel possible)
- **Driver generation** - 2-5 minutes for new source
- **Memory efficient** - DuckDB runs in-process
- **Scalable** - Can handle 100+ campaigns easily

## Future Enhancements (Post-MVP)

### Planned Features
- **Multi-version drivers** - Track and compare different driver versions
- **Error recovery** - Automatic retry with backoff
- **Data validation** - Schema validation and data quality checks
- **Caching strategy** - Intelligent cache invalidation
- **Webhooks** - Push notifications on data changes
- **Scheduled extraction** - Periodic automatic refreshes
- **Driver marketplace** - Share drivers across organizations

### Technology Upgrades
- **MotherDuck** - Cloud DuckDB for multi-user access
- **Docker Compose** - One-command environment setup
- **Kubernetes** - Production deployment support
- **GraphQL API** - More flexible query interface
- **Real-time streaming** - WebSocket updates

## Troubleshooting

### Mock Servers Not Starting
```bash
# Kill any processes on ports 3001, 3003, 3004, 5001, 8000
lsof -ti:3001,3003,3004,5001,8000 | xargs kill -9

# Restart
./start-all-mocks.sh
```

### DuckDB Lock Error
```bash
# DuckDB file may be locked
rm pipelines/nike_campaigns.duckdb

# Re-extract data
cd pipelines && python nike_campaigns_pipeline.py
```

### Driver Generation Fails
- Check API endpoint is responding
- Verify authentication headers
- Check response format is valid JSON
- Review logs in agent.py output

## Contact & Support

This is a hackathon MVP built to demonstrate autonomous data integration capabilities. All components are functional and ready for demo/testing.

---

**Built with:** Python, Node.js, TypeScript, dlthub, DuckDB, Svelte
**Status:** 24-hour MVP, fully functional
**Last Updated:** November 11, 2025
