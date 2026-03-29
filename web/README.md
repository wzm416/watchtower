# Watchtower web

Vite + React + TypeScript SPA: **Sign in with Google** (GIS), monitors table, add-monitor form (cron + optional NL hint via API).

## Setup

```bash
npm install
cp .env.example .env
```

Set **`VITE_GOOGLE_CLIENT_ID`** to your OAuth web client ID. Leave **`VITE_API_URL`** empty in development so `vite.config.ts` proxies `/api` and `/internal` to `http://127.0.0.1:8000`.

## Dev

```bash
npm run dev
```

Run the API on port 8000 (see `../api/README.md`).

## Build

```bash
npm run build
```

For production, set **`VITE_API_URL`** to the public API origin if the app is not served on the same host as the API.
