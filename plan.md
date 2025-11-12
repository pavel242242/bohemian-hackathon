# 24-Hour Hackathon MVP - Realistic Mock Architecture

## Core Concept
Agent orchestrates data from **real advertising platform APIs** (mocked) to answer: "Top 20 Nike campaigns, last 2 months, channels, budgets"

---

## Realistic Data Sources (All Mocked)

### 1. **Meta Ad Library API** (REST)
- **Real API:** `graph.facebook.com/ads_archive`
- **Our mock:** Returns Nike's FB/Instagram campaigns
- **Data:** Campaign name, creative, impressions, date range
- **Channel:** Facebook, Instagram

### 2. **Google Ads API** (REST)
- **Real API:** Google Ads Query Language
- **Our mock:** Returns Nike's YouTube/Display campaigns
- **Data:** Campaign name, budget, clicks, conversions
- **Channel:** YouTube, Google Display, Search

### 3. **TikTok Ads API** (REST)
- **Real API:** `business-api.tiktok.com/open_api/v1.3/`
- **Our mock:** Returns Nike's TikTok campaigns
- **Data:** Campaign name, spend, views, engagement
- **Channel:** TikTok

### 4. **Budget Approval System** (SOAP/XML)
- **Simulates:** Enterprise finance system
- **Data:** Campaign IDs, approved budgets, approval dates
- **Purpose:** Cross-reference budget data with campaigns

---

## Implementation Phases (24h)

### Phase 1: Mock Servers (6-7h)

**1.1 Research Real APIs** (1h)
- Document actual API structures from Meta, Google, TikTok
- Create realistic response schemas

**1.2 Realistic Fixtures** (2h)
- Mix of real Nike campaigns (Air Max Day, Just Do It) + invented
- Realistic budgets: $500K - $3M
- Last 2 months date ranges
- 20 total campaigns across platforms

**1.3 Build Mocks** (3-4h)
- **Meta:** json-server on port 3001
- **Google Ads:** FastAPI on port 3002
- **TikTok:** Express on port 3003
- **SOAP Budget:** Flask + spyne on port 3004

### Phase 2: dlthub Connectors (4-5h)

**Custom sources for each API:**
- `pipelines/sources/meta_ads.py`
- `pipelines/sources/google_ads.py`
- `pipelines/sources/tiktok_ads.py`
- `pipelines/sources/budget_soap.py`

**Unified pipeline to MotherDuck**

### Phase 3: Agent Orchestration (4-5h)

**Backend (TypeScript):**
- Parse user query
- Determine sources to query
- Execute dlthub pipelines
- Aggregate results from MotherDuck
- REST API endpoints

### Phase 4: Testing (3-4h)

- Mock server validation
- dlthub pipeline tests
- End-to-end integration tests

### Phase 5: UI (4-5h)

**SvelteKit:**
- Query input form
- Results table (campaigns, channels, budgets)
- Real-time logs panel

### Phase 6: Integration (2-3h)

- Docker Compose for all mocks
- Demo script preparation
- Bug fixes

---

## Tech Stack

**Backend:** Node.js + TypeScript + Express
**Agent:** Claude API (direct)
**Data Extraction:** dlthub (Python)
**Storage:** MotherDuck (DuckDB)
**Mocks:** json-server, FastAPI, Express, Flask
**Frontend:** SvelteKit + Tailwind
**Testing:** Jest/Vitest + Supertest

---

## Demo Flow

1. User: "Top 20 Nike campaigns, last 2 months, channels, budgets"
2. Agent logs: "Querying Meta Ad Library... 8 campaigns found"
3. Agent logs: "Querying Google Ads API... 7 campaigns found"
4. Agent logs: "Querying TikTok Ads API... 5 campaigns found"
5. Agent logs: "Cross-referencing budgets via SOAP... 18 matched"
6. Results: Top 20 aggregated campaigns with all details

---

## Key Deliverables

✅ 4 realistic mock APIs (Meta, Google, TikTok, SOAP)
✅ dlthub pipelines for each source
✅ Agent orchestration logic
✅ MotherDuck aggregation
✅ Working UI
✅ Full test suite
✅ Docker Compose setup
✅ Demo-ready in 24h

---

## Project Structure

```
STAGEHAND/
├── mocks/
│   ├── meta-api/
│   │   ├── meta-ads.json          # Realistic Meta responses
│   │   ├── routes.json
│   │   └── Dockerfile
│   ├── google-ads/
│   │   ├── server.py              # FastAPI mock
│   │   ├── fixtures.json
│   │   └── Dockerfile
│   ├── tiktok-api/
│   │   ├── server.js              # Express mock
│   │   ├── fixtures.json
│   │   └── Dockerfile
│   └── soap-budget/
│       ├── soap_server.py         # Flask + spyne
│       ├── approvals.xml
│       └── Dockerfile
├── pipelines/
│   ├── sources/
│   │   ├── meta_ads.py
│   │   ├── google_ads.py
│   │   ├── tiktok_ads.py
│   │   └── budget_soap.py
│   ├── nike_campaigns_pipeline.py
│   └── requirements.txt
├── backend/
│   ├── src/
│   │   ├── agent.ts
│   │   ├── storage.ts
│   │   └── server.ts
│   └── package.json
├── ui/
│   └── src/routes/+page.svelte
├── docker-compose.yml
└── README.md
```

---

## Architecture Insights (From Codex Second Opinion)

**Key Warnings:**
- Too many integration points can break demo - mock heavily
- Focus on orchestration, not real scraping
- Prioritize dlthub integration over custom connectors
- Keep UI minimal - single page app

**Recommendations:**
- Use json-server for REST mocks (fastest)
- DuckDB/MotherDuck combo for SQL semantics
- Light integration tests > full coverage
- Define fixtures first, then build mocks

**Risk Mitigations:**
- Mock scraping output to avoid debugging Stagehand
- Template-based agent prompts to reduce errors
- Local DuckDB fallback if MotherDuck issues
- Docker Compose for easy mock orchestration

---

## YAGNI for v2 (Post-Hackathon)

- ❌ Real web scraping
- ❌ Multiple data extractors (airbyte/keboola)
- ❌ Discovery agent (separate service)
- ❌ Parallel scraping optimization
- ❌ Confidence scores
- ❌ Fancy UI animations
- ❌ User-triggered data ingestion
