# Nike Campaigns Query Interface

## Quick Start

You can now "talk" to your Nike campaigns data!

### Option 1: Ask a Question (One-shot)

```bash
cd /Users/chocho/projects/STAGEHAND/pipelines
source venv/bin/activate
python query.py "Show me the top 20 Nike campaigns"
```

### Option 2: Interactive Mode

```bash
python query.py
```

Then ask questions:
```
🔍 Your question: Show me the top campaigns
🔍 Your question: What are the recent campaigns?
🔍 Your question: Show campaigns with budgets
```

Type `refresh` to re-extract fresh data
Type `quit` or `exit` to quit

## Example Questions

**Top campaigns:**
```bash
python query.py "Show me the top 20 Nike campaigns"
python query.py "What are the highest budget campaigns?"
```

**Recent campaigns:**
```bash
python query.py "Show me recent Nike campaigns"
python query.py "What are the latest campaigns?"
```

**By channel:**
```bash
python query.py "Show me campaigns by channel"
python query.py "What platforms are running Nike ads?"
```

## What It Does

1. **Extracts data** from all 4 sources:
   - Meta Ad Library (Facebook/Instagram)
   - Google Ads API
   - TikTok Ads API
   - SOAP Budget Approval System

2. **Loads into DuckDB** for fast SQL queries

3. **Queries and displays** results in a nice table

4. **Shows summary** with sources and channels used

## Output Example

```
======================================================================
  RESULTS: Show me the top 20 Nike campaigns
======================================================================

               campaign_name source            channel   budget  impressions
    Unlimited Athlete Series Google     Google Display $2000.0K      5600000
   Spring Running Collection TikTok             TikTok $1500.0K     45230000
    Just Do It Marathon 2025 Google            YouTube $1500.0K      4250000

📊 Total: 20 campaigns

💰 SUMMARY:
   Sources: Google, TikTok, Meta
   Channels: Google Display, TikTok, Facebook/Instagram, YouTube, Search
```

## Behind the Scenes

- **Mocks**: All 4 advertising platform APIs (running on localhost)
- **dlthub**: Extracts and normalizes data from each source
- **DuckDB**: Stores aggregated campaign data
- **Query Interface**: Simple CLI that runs SQL queries

## Next Steps

Want to build:
- **Backend API** - Make this accessible via REST API
- **Web UI** - Connect the SvelteKit interface
- **Smart Agent** - Use Claude to parse queries intelligently
- **Live Logs** - Stream extraction progress in real-time

Let me know what you want to build next!
