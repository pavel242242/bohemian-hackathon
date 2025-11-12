# STAGEHAND - Quick Start Guide

Get the Nike campaigns demo running in under 5 minutes!

## What's Been Built (So Far)

✅ **4 Mock Servers** - All realistic advertising platform APIs
✅ **Backend API** - TypeScript + Express server
✅ **UI** - Minimal SvelteKit interface
⏳ **dlthub Connectors** - Next step
⏳ **Agent Orchestration** - Next step
⏳ **MotherDuck Integration** - Next step

## Quick Test (Right Now!)

### Step 1: Start All Mock Servers

```bash
cd /Users/chocho/projects/STAGEHAND
./start-all-mocks.sh
```

This starts:
- Meta Ad Library Mock (port 3001) - 8 Nike campaigns
- Google Ads Mock (port 8000) - 7 Nike campaigns
- TikTok Ads Mock (port 3003) - 5 Nike campaigns
- SOAP Budget Mock (port 5001) - 20 budget approvals

### Step 2: Test the Mocks

```bash
./test-all-mocks.sh
```

You should see:
```
✓ All mock servers are working!
```

### Step 3: Test Individual Endpoints

```bash
# Meta campaigns
curl http://localhost:3001/ads_archive | python3 -m json.tool

# Google campaigns
curl http://localhost:8000/campaigns | python3 -m json.tool

# TikTok campaigns
curl http://localhost:3003/open_api/v1.3/campaign/get/ | python3 -m json.tool

# SOAP health check
curl http://localhost:5001/health
```

### Step 4: Start Backend (Optional for now)

```bash
cd backend
npm install
npm run dev
```

Backend will run on http://localhost:4000

Test it:
```bash
curl http://localhost:4000/health
curl http://localhost:4000/api/campaigns
```

### Step 5: Start UI (Optional for now)

```bash
cd ui
npm install
npm run dev
```

UI will run on http://localhost:5173

Open in browser and enter query: "Top 20 Nike campaigns, last 2 months"

## Stop Everything

```bash
./stop-all-mocks.sh
```

## What Each Mock Contains

### Meta Ad Library (8 campaigns)
- Air Max Day - $2.5M budget
- Nike By You - $1.2M budget
- Women's Basketball - $1.1M budget
- Run with Pegasus - $850K budget
- Fall Collection - $1.5M budget
- Just Do It - $1.8M budget
- Retro Sneaker - $780K budget
- Training Club - $1.15M budget

### Google Ads (7 campaigns)
- Just Do It Marathon - $1.5M budget (YouTube)
- Air Innovations - $950K budget (Display)
- Find Your Greatness - $1.2M budget (Search)
- React Performance - $700K budget (YouTube)
- Unlimited Athlete - $2M budget (Display)
- Peak Performance - $1.1M budget (Search)
- Innovation Hub - $800K budget (YouTube)

### TikTok Ads (5 campaigns)
- Spring Running Collection - $1.5M budget
- Air Max Hype - $850K budget
- Jordan Legacy - $750K budget
- Women's Sportswear - $950K budget
- Youth Basketball - $550K budget

### SOAP Budget Approvals (20 records)
Cross-references all campaigns above with approval dates, cost centers, approvers

## Next Steps

Now that mocks are working, we need to:

1. **Create dlthub connectors** - Extract data from each mock
2. **Set up MotherDuck** - Store aggregated campaign data
3. **Build agent** - Orchestrate data extraction based on user query
4. **Connect UI to backend** - Display results in table
5. **Add real-time logs** - Show agent activity

## File Structure

```
STAGEHAND/
├── mocks/
│   ├── meta-api/        ✅ Meta Ad Library mock
│   ├── google-ads/      ✅ Google Ads mock
│   ├── tiktok-api/      ✅ TikTok Ads mock
│   └── soap-budget/     ✅ SOAP budget mock
├── backend/             ✅ TypeScript + Express API
├── ui/                  ✅ SvelteKit interface
├── pipelines/           ⏳ dlthub connectors (TODO)
├── start-all-mocks.sh   ✅ Start all mocks
├── stop-all-mocks.sh    ✅ Stop all mocks
├── test-all-mocks.sh    ✅ Test all mocks
└── plan.md              ✅ Full implementation plan
```

## Troubleshooting

**Port already in use?**
```bash
./stop-all-mocks.sh
./start-all-mocks.sh
```

**Mock not responding?**
```bash
# Check logs
cat logs/meta-mock.log
cat logs/google-mock.log
cat logs/tiktok-mock.log
cat logs/soap-mock.log
```

**Need to restart one mock?**
```bash
# Example: restart Meta mock
lsof -ti:3001 | xargs kill -9
cd mocks/meta-api && npm start
```

## Ready to Continue Building?

You now have all 4 mock servers running with realistic Nike campaign data!

The next phase is to build the dlthub connectors to extract this data and aggregate it in MotherDuck.
