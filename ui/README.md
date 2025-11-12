# Nike Campaigns Demo - UI

A minimal SvelteKit frontend for testing Nike campaigns queries against the Stagehand backend.

## Features

- Query input textarea with default Nike campaign query
- Submit button to send queries to the backend
- Results table showing campaign data (name, channel, budget)
- Live logs panel showing agent activity
- Clean, responsive UI built with Tailwind CSS
- TypeScript support throughout

## Project Structure

```
src/
├── main.ts                 # Application entry point
├── app.svelte              # Root app component
├── app.css                 # Global styles (Tailwind imports)
├── routes/
│   └── +page.svelte        # Main page with query interface
└── lib/
    └── api.ts              # Backend API client

Configuration files:
├── vite.config.ts          # Vite bundler config
├── tsconfig.json           # TypeScript config
├── tailwind.config.js       # Tailwind CSS config
├── postcss.config.js        # PostCSS config
└── package.json            # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Install dependencies:
```bash
cd /Users/chocho/projects/STAGEHAND/ui
npm install
```

2. Start the development server:
```bash
npm run dev
```

The dev server will open automatically at `http://localhost:5173`

### Building for Production

```bash
npm run build
npm run preview
```

## Development

The UI expects the backend API to be running on `http://localhost:4000` and to accept POST requests to `/query` with the following format:

```json
{
  "query": "Your campaign query here"
}
```

The API should respond with:

```json
{
  "campaigns": [
    {
      "id": "campaign-1",
      "name": "Campaign Name",
      "channel": "Social Media",
      "budget": 10000
    }
  ]
}
```

### Making Changes

- **Query Component**: Edit `src/routes/+page.svelte` to modify the UI layout
- **API Client**: Update `src/lib/api.ts` to change backend integration
- **Styling**: Modify Tailwind classes in component files or update `tailwind.config.js`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run check` - Run Svelte type checking

## Dependencies

- **Svelte 4** - UI framework
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS & Autoprefixer** - CSS processing

## Notes

- The UI is intentionally minimal and focused on demonstrating the query/response flow
- Results table automatically adapts to response data structure
- Logs panel shows real-time feedback during API calls
- All components are responsive and mobile-friendly
