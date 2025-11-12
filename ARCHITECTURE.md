# STAGEHAND Architecture

**Intelligent Nike Campaigns Query System with Dynamic Driver Generation**

A 24-hour hackathon project that autonomously generates data pipeline drivers for APIs, enabling unified querying of multi-platform ad campaign data. Built with Python, dlthub, DuckDB, Express.js, and Svelte.

## Table of Contents

1. [System Overview](#system-overview)
2. [Technical Stack](#technical-stack)
3. [Core Innovation: Dynamic Driver Generation](#core-innovation-dynamic-driver-generation)
4. [Agent Architecture](#agent-architecture)
5. [Data Flow](#data-flow)
6. [Component Details](#component-details)
7. [API Integrations](#api-integrations)
8. [Database Schema](#database-schema)
9. [Deployment](#deployment)

---

## System Overview

STAGEHAND is composed of four main components that work together to query Nike campaigns across multiple advertising platforms:

### 1. Mock API Servers (Express.js)
Simulates real advertising platform APIs with realistic features like pagination, rate limiting, and complex response formats. These serve as both demonstration and testing infrastructure.

**Servers:**
- **Meta Ads API** (Port 3001): Facebook/Instagram Ad Library mock
- **Google Ads API** (Port 8000): Google Ads campaign mock
- **TikTok Ads API** (Port 3003): TikTok campaign mock
- **Seznam Ads API** (Port 3004): Complex Czech advertising platform with nested pagination
- **SOAP Budget Service** (Port 5001): SOAP-based budget approval service

### 2. Data Pipelines (dlthub + Python)
Extracts campaign data from APIs using dlthub sources and loads into DuckDB. Dynamically generates drivers for new APIs based on pattern discovery.

**Key Files:**
- `nike_campaigns_pipeline.py`: Main pipeline orchestrator
- `agent.py`: Intelligent query agent with natural language parsing
- `driver_manager.py`: Dynamic driver generation and testing
- `api_explorer.py`: API pattern discovery
- `source_generator.py`: Code generation from patterns
- `sources/`: Individual source adapters

### 3. Backend API (Express.js)
RESTful gateway serving as bridge between frontend and Python data pipelines. Handles query routing and pipeline execution.

**Endpoints:**
- `GET /health`: Server health check
- `GET /api/campaigns`: Query campaigns (proxies to mock servers)
- `POST /api/query`: Execute natural language queries
- `POST /api/refresh`: Trigger data pipeline refresh
- `GET /api/status`: System status and mock server health

### 4. Frontend UI (Svelte + Vite)
Interactive interface for submitting natural language queries and viewing results with real-time logging.

**Features:**
- Natural language query input
- Live result display
- System status monitoring
- Data refresh controls
- Real-time log streaming

---

## Technical Stack

### Data & Analytics
- **dlthub**: Data load tool for building ELT pipelines
- **DuckDB**: Embedded SQL database for unified data views
- **Python 3.9+**: Scripting language for agents and generators

### Backend
- **Express.js**: REST API framework
- **TypeScript**: Type-safe backend code
- **axios**: HTTP client for API calls

### Frontend
- **Svelte**: Component-based UI framework
- **Vite**: Build tool
- **Tailwind CSS**: Utility-first styling

### Infrastructure
- **Node.js**: Runtime for mock servers and backend
- **Docker**: Optional containerization
- Shell scripts: Orchestration (`start-all-mocks.sh`, `stop-all-mocks.sh`)

---

## Core Innovation: Dynamic Driver Generation

The system's main innovation is the **autonomous driver generation system** that discovers API patterns and generates working data pipeline adapters without manual intervention.

### Three-Module Architecture

#### 1. API Explorer (`api_explorer.py`)

Discovers API characteristics through endpoint exploration.

**Responsibilities:**
- Make initial requests to discover response format
- Detect pagination patterns (cursor, offset, page-based)
- Identify rate limiting headers
- Analyze response nesting and data locations
- Detect primary key fields

**Key Methods:**
```python
APIExplorer.explore(initial_endpoint, headers)
  -> {
      'auth': 'required' | None,
      'pagination': {'type': 'cursor|offset|page|none', ...},
      'response_format': {'type': 'standard|wrapped', ...},
      'rate_limiting': {...} | None,
      'data_path': 'data.campaigns',
      'primary_key': 'id'
    }
```

**Pattern Detection Examples:**
- **Pagination**: Cursor tokens, offset/limit, page numbers
- **Response Format**: Wrapped in `responseMetadata`, nested structures
- **Data Paths**: `data`, `results`, `items`, nested hierarchies
- **Primary Keys**: `id`, `_id`, `campaignId`, etc.

#### 2. Source Generator (`source_generator.py`)

Generates complete dlthub source code from discovered patterns.

**Responsibilities:**
- Generate imports and decorators
- Create function signatures with parameters
- Build pagination loops for detected pattern
- Implement rate limit checking
- Handle response unwrapping

**Generated Code Features:**
- Automatic pagination handling based on type
- Rate limiting awareness
- Response status validation
- Error handling
- Batch item processing with yield

**Example Generated Function:**
```python
@dlt.resource(
    name="seznam_campaigns",
    write_disposition="merge",
    primary_key="campaignId"
)
def seznam_campaigns(base_url="http://localhost:3004", api_key="..."):
    """Auto-generated source with cursor pagination"""
    headers = {'X-Seznam-Api-Key': api_key}

    cursor = None
    page = 1

    while True:
        params = {'page': page, 'pageSize': 10}
        if cursor:
            params['cursor'] = cursor

        response = requests.get(f"{base_url}/api/v2/campaigns", ...)
        data = response.json()

        items = data.get('data', {}).get('campaigns', [])
        if not items:
            break

        for item in items:
            yield item

        has_next = data.get('pagination', {}).get('navigation', {}).get('hasNext')
        if not has_next:
            break

        cursor = data.get('pagination', {}).get('navigation', {}).get('nextCursor')
        page += 1
```

#### 3. Driver Manager (`driver_manager.py`)

Manages iterative driver generation with self-healing and testing.

**Responsibilities:**
- Coordinate API exploration and code generation
- Test generated drivers by importing and executing
- Analyze failures and refine patterns
- Persist working drivers to disk
- Track generation attempts

**Iterative Refinement Loop:**

```
1. Explore API (APIExplorer)
        ↓
2. Generate Driver Code (SourceGenerator)
        ↓
3. Test Driver (Try Import & Execute)
        ↓
   Success? ──→ YES ──→ Save & Return ✅
   └─→ NO
        ↓
4. Analyze Error & Refine Patterns
        ↓
5. Max Attempts? ──→ YES ──→ Return Error ❌
   └─→ NO ──→ Retry from Step 2
```

**Self-Healing Strategies:**
- **KeyError**: Try alternative data paths (`data`, `results`, `items`)
- **AttributeError**: Switch from wrapped to standard response format
- **Auth Errors**: Mark authentication as required
- **Pagination Issues**: Fall back to simpler pagination patterns

**Key Methods:**
```python
DriverManager.build_driver(source_name, base_url, endpoint, headers)
  -> (success: bool, driver_path: Path, error: str)

DriverManager.driver_exists(source_name)
  -> bool
```

---

## Agent Architecture

The intelligent query agent (`agent.py`) orchestrates the entire system, handling natural language understanding, data freshness decisions, and result formatting.

### Main Flow

```
User Query (Natural Language)
    ↓
1. Parse Intent & Extract Requirements
    ├─ Identify data sources needed
    ├─ Extract filters (budget, date range, etc.)
    ├─ Determine if fresh data needed
    └─ Detect special requirements (scraping, etc.)
    ↓
2. Check & Build Drivers
    ├─ For each source:
    │  ├─ Check if driver exists
    │  ├─ Build if missing (via DriverManager)
    │  └─ Track build status
    └─ Log any failures
    ↓
3. Check Data Status
    ├─ Test if DuckDB exists
    ├─ Count rows in tables
    ├─ Check modification time
    └─ Determine freshness
    ↓
4. Decide Action
    ├─ If no data: REFRESH (build pipeline)
    ├─ If stale and fresh requested: REFRESH
    ├─ If scraping needed: SCRAPE
    └─ Otherwise: QUERY
    ↓
5. Execute Action
    ├─ REFRESH: Run nike_campaigns_pipeline.py
    ├─ QUERY: Execute unified SQL query
    └─ Return formatted results
    ↓
Results (Formatted Text Output)
```

### Query Parsing

Natural language is parsed into structured intent with:

```python
{
    'intent': 'query' | 'refresh' | 'scrape',
    'sources': ['meta', 'google', 'tiktok', 'seznam', 'soap'],
    'filters': {
        'budget_min': 1000,
        'month': 12,
        'year': 2025,
        'sort_by': 'budget_desc' | 'date_desc'
    },
    'limit': 20,
    'needs_fresh_data': False,
    'scrape_web': False
}
```

**Recognized Patterns:**
- **Sources**: "meta", "facebook", "google", "adwords", "tiktok", "seznam", "czech", "budget", "soap"
- **Freshness**: "latest", "recent", "fresh", "new", "update", "refresh"
- **Sorting**: "highest", "largest", "biggest", "most expensive", "newest"
- **Filters**: Budget amounts (`$5000`), dates (December, 2025)

### Unified Query

Once drivers are built and data refreshed, agent executes a unified SQL query across all sources:

```sql
SELECT
    campaign_name,
    source,
    channel,
    budget,
    impressions,
    start_date,
    end_date
FROM (
    SELECT ... FROM marketing_data.meta_campaigns
    UNION ALL
    SELECT ... FROM marketing_data.google_campaigns
    UNION ALL
    SELECT ... FROM marketing_data.tiktok_campaigns
    UNION ALL
    SELECT ... FROM marketing_data.seznam_campaigns
)
WHERE [filters applied]
ORDER BY [sort criteria]
LIMIT [limit]
```

---

## Data Flow

### High-Level Workflow

```
┌─────────────────┐
│   Frontend UI   │
│   (Svelte)      │
└────────┬────────┘
         │ Natural language query
         ↓
┌─────────────────────┐
│  Backend API        │
│  (Express.js)       │
│  Port 4000          │
└────────┬────────────┘
         │ POST /api/query
         ↓
┌──────────────────────────────┐
│  Agent (agent.py)            │
│  • Parse query               │
│  • Check drivers             │
│  • Decide action             │
│  • Execute pipeline or query │
└────────┬─────────────────────┘
         │
    ┌────┴─────────────────────────────────┐
    │                                       │
    ↓                                       ↓
┌──────────────────┐         ┌──────────────────────────┐
│ Data Pipelines   │         │ DuckDB Database          │
│ (dlthub)         │         │ nike_campaigns.duckdb    │
│                  │         │                          │
│ Sources:         │         │ Tables:                  │
│ • meta_ads       │         │ • marketing_data.meta_   │
│ • google_ads     │────────→│   campaigns              │
│ • tiktok_ads     │         │ • marketing_data.google_ │
│ • seznam_ads     │         │   campaigns              │
│ • budget_        │         │ • marketing_data.tiktok_ │
│   approvals      │         │   campaigns              │
└──────────────────┘         │ • marketing_data.seznam_ │
    ↑       ↑                │   campaigns              │
    │       │                │ • marketing_data.budget_ │
    │       │                │   approvals              │
    │       │                └──────┬───────────────────┘
    │       └─────────────────────────┘
    │                │ SQL Query
    │                ↓
    │            Unified Results
    │                │
    └────────────────┘ Fetch if missing
```

### Specific Data Flows

#### 1. Fresh Query Flow (Data Exists)

```
User Query
    ↓
Agent parses intent
    ↓
Check database → EXISTS & FRESH
    ↓
Execute SQL query on existing data
    ↓
Format results → Display
```

#### 2. Refresh Flow (Data Missing/Stale)

```
User Query
    ↓
Agent parses intent
    ↓
Check database → MISSING or STALE
    ↓
Check/build drivers for sources
    ↓
Run nike_campaigns_pipeline.py
    ├─ Load meta_ads source → DuckDB
    ├─ Load google_ads source → DuckDB
    ├─ Load tiktok_ads source → DuckDB
    ├─ Load seznam_ads source → DuckDB
    └─ Load budget_approvals → DuckDB
    ↓
Execute SQL query on new data
    ↓
Format results → Display
```

#### 3. Dynamic Driver Build Flow

```
Query requests new API (source not in hardcoded list)
    ↓
DriverManager.build_driver() called
    ↓
APIExplorer discovers patterns
    ├─ Makes requests to base_url + endpoint
    ├─ Analyzes response structure
    ├─ Detects pagination type
    ├─ Identifies data paths
    └─ Returns patterns dict
    ↓
SourceGenerator.generate() creates code
    ├─ Generates imports
    ├─ Creates @dlt.resource decorator
    ├─ Builds function signature
    ├─ Generates pagination loop
    └─ Returns Python code string
    ↓
Driver saved to pipelines/sources/[source]_ads.py
    ↓
DriverManager tests driver
    ├─ Dynamically import module
    ├─ Call resource function
    ├─ Iterate first 3 items
    └─ Verify success
    ↓
If success → Return (True, path, None)
If failure → Refine patterns → Retry (max 3x)
```

---

## Component Details

### Backend API Structure

**File:** `/backend/src/server.ts`

```typescript
Express Server
├─ Port: 4000 (configurable via PORT env var)
├─ CORS: Enabled for cross-origin requests
├─ Endpoints:
│  ├─ GET /health → Server health status
│  ├─ GET /api/campaigns → Query mock servers
│  └─ GET /api/ads_archive → Direct archive proxy
└─ Middleware:
   ├─ CORS
   ├─ JSON parser
   └─ Error handlers
```

**Key Integrations:**
- Proxies requests to Meta mock server (`META_MOCK_SERVER` env var)
- Transforms responses into consistent API format
- Handles authentication and error translation

### Frontend Components

**File:** `/ui/src/app.svelte`

**Sections:**
1. **Status Bar**: Shows system readiness and mock server health
2. **Query Panel**: Text input for natural language queries
3. **Results Panel**: Displays formatted campaign data
4. **Logs Panel**: Real-time operation logs with timestamps
5. **Summary**: Campaign count, sources, channels, budget totals

**Reactive States:**
- `query`: User's input text
- `loading`: Whether query is executing
- `refreshing`: Whether pipeline is running
- `logs`: Array of timestamped log messages
- `resultOutput`: Formatted results text
- `summary`: Aggregated campaign statistics

### Data Source Adapters

#### Meta Ads Source (`sources/meta_ads.py`)
- Queries Meta Ad Library mock
- Extracts campaign budgets and impressions
- Maps fields to unified schema

#### Google Ads Source (`sources/google_ads.py`)
- Queries Google Ads mock
- Converts budget from micros to USD
- Handles channel information

#### TikTok Ads Source (`sources/tiktok_ads.py`)
- Queries TikTok API mock
- Extracts campaign metrics
- Maps impressions and budget

#### Seznam Ads Source (`sources/seznam_ads.py`) - Complex Enrichment
Most sophisticated source demonstrating dynamic driver capabilities:
- **Pagination**: Cursor-based with nested structure
- **Response Format**: Non-standard wrapped in `responseMetadata`
- **Enrichment**: Three separate API calls per campaign
  1. Campaigns endpoint: Basic campaign data
  2. Ads endpoint: Get ads within campaign
  3. Stats endpoint: Get performance metrics
- **Aggregation**: Combines multi-endpoint data into single record
- **Currency**: Converts CZK to USD

### Pipeline Orchestration

**File:** `nike_campaigns_pipeline.py`

Orchestrates loading from all sources:

```python
pipeline = dlt.pipeline(
    pipeline_name="nike_campaigns",
    destination="duckdb",
    dataset_name="marketing_data"
)

# For each source:
pipeline.run(source_function(), table_name="...")
```

Supports:
- Partial failures (one source down doesn't stop others)
- Merge write disposition (idempotent updates)
- Detailed logging per source

---

## API Integrations

### Mock API Specifications

#### Meta Ads API (Port 3001)
```
GET /ads_archive?search=nike&limit=10&offset=0&after=cursor
Response:
{
  "ads": [{
    "ad_id": "string",
    "page_name": "string",
    "ad_text": "string",
    "spend": { "upper_bound": number },
    "impressions": { "upper_bound": number },
    "ad_delivery_start_time": "ISO string",
    "ad_delivery_stop_time": "ISO string"
  }]
}
```

#### Google Ads API (Port 8000)
```
GET /campaigns?limit=50&page=1
Response:
{
  "campaigns": [{
    "id": "string",
    "name": "string",
    "budget_micros": number,
    "channel": "string",
    "metrics": {
      "impressions": number,
      "clicks": number
    },
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  }]
}
```

#### TikTok Ads API (Port 3003)
```
GET /campaigns?limit=20
Response:
{
  "data": [{
    "campaign_id": "string",
    "campaign_name": "string",
    "budget": number,
    "status": "ACTIVE|PAUSED",
    "metrics": {
      "impressions": number,
      "clicks": number
    },
    "start_time": "ISO string",
    "end_time": "ISO string"
  }]
}
```

#### Seznam Ads API (Port 3004) - Complex
```
GET /api/v2/campaigns?page=1&pageSize=10&cursor=optional
Headers: X-Seznam-Api-Key: demo_api_key_12345

Response:
{
  "responseMetadata": {
    "status": "SUCCESS",
    "requestId": "string",
    "timestamp": "ISO string"
  },
  "pagination": {
    "currentPage": { "size": number, "index": number },
    "navigation": {
      "hasNext": boolean,
      "nextCursor": "base64|null",
      "hasPrevious": boolean,
      "totalElements": number,
      "totalPages": number
    }
  },
  "data": {
    "campaigns": [{
      "campaignId": "string",
      "name": "string",
      "status": "ACTIVE|PAUSED",
      "dailyBudgetCZK": number,
      "created": "ISO string",
      "updated": "ISO string"
    }]
  }
}

GET /api/v2/campaigns/{campaignId}/ads
Response:
{
  "responseMetadata": { "status": "SUCCESS" },
  "data": {
    "ads": [{
      "adId": "string",
      "title": "string",
      "clicks": number,
      "impressions": number,
      "ctr": number
    }]
  }
}

GET /api/v2/campaigns/{campaignId}/stats
Response:
{
  "responseMetadata": { "status": "SUCCESS" },
  "data": {
    "statistics": {
      "totalSpend": number,
      "avgCPC": number,
      "conversions": number,
      "conversionRate": number
    },
    "currency": "CZK",
    "period": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" }
  }
}
```

#### SOAP Budget Service (Port 5001)
SOAP-based service for budget approval workflows. Implemented as Python SOAP server with complex XML handling.

---

## Database Schema

### DuckDB Structure

**Database:** `nike_campaigns.duckdb`
**Dataset Schema:** `marketing_data`

#### meta_campaigns Table
```
id (VARCHAR)
page_name (VARCHAR)
ad_text (VARCHAR)
spend__upper_bound (DOUBLE)
impressions__upper_bound (INTEGER)
ad_delivery_start_time (TIMESTAMP)
ad_delivery_stop_time (TIMESTAMP)
_dlt_load_id (VARCHAR) [dlthub metadata]
_dlt_id (VARCHAR) [dlthub metadata]
```

#### google_campaigns Table
```
id (VARCHAR)
name (VARCHAR)
budget_micros (DOUBLE)
channel (VARCHAR)
metrics__impressions (INTEGER)
metrics__clicks (INTEGER)
start_date (DATE)
end_date (DATE)
_dlt_load_id (VARCHAR)
_dlt_id (VARCHAR)
```

#### tiktok_campaigns Table
```
campaign_id (VARCHAR)
campaign_name (VARCHAR)
budget (DOUBLE)
status (VARCHAR)
metrics__impressions (VARCHAR)
start_time (TIMESTAMP)
end_time (TIMESTAMP)
_dlt_load_id (VARCHAR)
_dlt_id (VARCHAR)
```

#### seznam_campaigns Table
```
campaignId (VARCHAR)
name (VARCHAR)
status (VARCHAR)
dailyBudgetCZK (DOUBLE)
created (TIMESTAMP)
updated (TIMESTAMP)
ads (STRUCT[]) [nested]
totalClicks (INTEGER)
totalImpressions (INTEGER)
avgCTR (DOUBLE)
totalSpend (DOUBLE)
avgCPC (DOUBLE)
conversions (INTEGER)
conversionRate (DOUBLE)
currency (VARCHAR)
budgetCZK (DOUBLE)
estimatedMonthlyBudget (DOUBLE)
_dlt_load_id (VARCHAR)
_dlt_id (VARCHAR)
```

#### budget_approvals Table
```
id (VARCHAR)
campaign_id (VARCHAR)
requested_budget (DOUBLE)
approved_budget (DOUBLE)
status (VARCHAR)
approval_date (TIMESTAMP)
_dlt_load_id (VARCHAR)
_dlt_id (VARCHAR)
```

### Unified Query View

The agent constructs a dynamic UNION query across all tables, handling schema differences:

```sql
-- Normalize different field names
-- Convert different currencies
-- Align date formats
-- Filter and sort based on intent
```

Key transformations:
- **Budget**: Convert CZK to USD (~25:1 ratio)
- **Timestamps**: Cast different date formats to TIMESTAMP
- **Null handling**: COALESCE missing metrics
- **Impressions**: Cast to INTEGER, handle missing values

---

## Deployment

### Quick Start

#### 1. Start Mock Servers
```bash
./start-all-mocks.sh
```

This script starts all mock servers on their configured ports:
- Meta: 3001
- Google: 8000
- TikTok: 3003
- Seznam: 3004
- SOAP Budget: 5001

#### 2. Set Up Python Environment
```bash
cd pipelines
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Start Backend Server
```bash
cd backend
npm install
npm run dev  # or: npx ts-node src/server.ts
```

Server runs on port 4000

#### 4. Start Frontend
```bash
cd ui
npm install
npm run dev
```

UI runs on port 5173 (Vite default)

#### 5. Refresh Data (First Time)
In the UI, click "Refresh Data" to run the pipeline and populate DuckDB.

### Environment Variables

**Backend (`backend/.env`):**
```
PORT=4000
META_MOCK_SERVER=http://localhost:3001
```

**Pipelines (`pipelines/.env`):**
```
DUCKDB_PATH=nike_campaigns.duckdb
```

### Stopping Services
```bash
./stop-all-mocks.sh
```

### Testing

Run mock server tests:
```bash
./test-all-mocks.sh
```

This validates:
- Each server responds to health checks
- Endpoints return expected data
- Pagination works correctly
- Authentication is enforced

---

## Design Patterns & Innovations

### 1. Autonomous Driver Generation
- **Pattern Discovery**: APIExplorer dynamically learns API characteristics
- **Code Generation**: SourceGenerator creates working pipelines from patterns
- **Self-Healing**: DriverManager refines patterns based on failures
- **Zero Manual Configuration**: New APIs work without writing source code

### 2. Unified Data Access
- **Multi-Source Abstraction**: Agent provides single interface to 5+ data sources
- **Schema Normalization**: Different field names and types are reconciled
- **Currency Conversion**: Automatic CZK ↔ USD conversion
- **Timestamp Alignment**: Different date formats normalized to TIMESTAMP

### 3. Intelligent Query Routing
- **Natural Language Understanding**: Parse intent from user queries
- **Data Freshness Awareness**: Decide between querying DB or refreshing
- **Capability Detection**: Know what data is available vs. missing
- **Graceful Degradation**: Work with partial source availability

### 4. Modular Architecture
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Each module has single responsibility
- **Testability**: Each component tested independently
- **Extensibility**: Easy to add new sources or query patterns

### 5. Real-Time Observability
- **Timestamped Logs**: Every operation tracked with precise timing
- **Status Monitoring**: Mock servers health visible in UI
- **Progress Tracking**: Users see each step of pipeline execution
- **Error Transparency**: Failures reported with context and suggestions

---

## Future Enhancements

### Planned Features
1. **Stagehand Integration**: Web scraping for additional campaign sources
2. **LLM-Based Agent**: Replace rule-based parsing with Claude/GPT
3. **Incremental Refresh**: Delta-loading instead of full refresh
4. **Caching Layer**: Redis for frequently-accessed queries
5. **Authentication Management**: Credential vault for API keys
6. **Rate Limit Coordination**: Batch requests across sources
7. **Data Validation**: Schema verification and data quality checks
8. **Export Formats**: CSV, JSON, Parquet export options

### Extensibility Points
- Add new mock servers (just create Express app on new port)
- Add new data sources (create Python file in `sources/`)
- Extend query parsing (add patterns to `agent.py`)
- Customize result formatting (update `_format_results()`)

---

## Hackathon Context

**Duration**: 24 hours
**Team Size**: Multi-disciplinary
**Challenge**: Build intelligent system to query multiple ad platforms without manual configuration

**Key Achievements**:
- ✅ Dynamic driver generation working end-to-end
- ✅ 5 data sources integrated (4 mocks + 1 SOAP)
- ✅ Complex API (Seznam) fully handled with enrichment
- ✅ Natural language query parsing
- ✅ Full-stack UI from frontend to backend to pipelines
- ✅ Real-time observability and logging

**Innovation Focus**:
The core innovation is **automatic driver generation** - discovering API patterns and generating working dlthub source code without manual intervention. This enables the system to handle new APIs by just specifying their base URL and endpoint.

---

## References

### Key Files
- **Agent**: `/pipelines/agent.py` (574 lines)
- **Driver Manager**: `/pipelines/driver_manager.py` (266 lines)
- **API Explorer**: `/pipelines/api_explorer.py` (284 lines)
- **Source Generator**: `/pipelines/source_generator.py` (375 lines)
- **Backend**: `/backend/src/server.ts` (164 lines)
- **Frontend**: `/ui/src/app.svelte` (217 lines)
- **Pipeline**: `/pipelines/nike_campaigns_pipeline.py` (212 lines)

### Running Examples

#### Query Top Campaigns
```bash
cd pipelines
python agent.py "Show me the top 20 Nike campaigns by budget"
```

#### Build Driver for New API
```python
from driver_manager import DriverManager

manager = DriverManager(Path("."))
success, path, error = manager.build_driver(
    source_name="my_api",
    base_url="https://api.example.com",
    endpoint="/campaigns",
    headers={"Authorization": "Bearer token"}
)
```

#### Direct DuckDB Query
```bash
duckdb nike_campaigns.duckdb
SELECT * FROM marketing_data.seznam_campaigns LIMIT 5;
```

---

**Last Updated**: November 11, 2025
**Status**: Complete for hackathon submission
