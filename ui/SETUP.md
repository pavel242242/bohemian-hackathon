# Quick Setup Guide

## One-time setup

1. Navigate to the UI directory:
```bash
cd /Users/chocho/projects/STAGEHAND/ui
```

2. Install dependencies (this will take a minute):
```bash
npm install
```

## Running the Development Server

```bash
npm run dev
```

This will:
- Install/verify dependencies
- Start Vite dev server on `http://localhost:5173`
- Automatically open your browser
- Watch for file changes and hot-reload

## Connecting to the Backend

1. Make sure your backend is running on `http://localhost:4000`
2. The backend should accept POST requests to `/query` with the format:
   ```json
   {
     "query": "Your query here"
   }
   ```

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│            Nike Campaigns Demo (Header)              │
├───────────────────┬─────────────────────────────────┤
│                   │                                 │
│  Query Input      │        Results Table            │
│  (textarea)       │      (campaign data)            │
│                   │                                 │
│  Submit Button    ├─────────────────────────────────┤
│                   │                                 │
│                   │      Logs Panel                 │
│                   │    (activity output)            │
│                   │                                 │
└───────────────────┴─────────────────────────────────┘
```

## Troubleshooting

- **Port 5173 already in use**: The dev server will automatically try the next available port
- **Backend connection errors**: Make sure the backend is running on `http://localhost:4000`
- **Styles not loading**: Tailwind will compile on first run, check browser console for errors

## Project Files

- `/src/routes/+page.svelte` - Main UI component (query input, results, logs)
- `/src/lib/api.ts` - Backend API client
- `/src/app.svelte` - Root app component
- `/tailwind.config.js` - Tailwind CSS configuration
