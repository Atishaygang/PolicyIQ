# PolicyIQ Frontend — V6

A clean, calm React interface for the PolicyIQ FastAPI backend.

The visual direction intentionally avoids a developer-dashboard or "AI neon" look. It uses warm neutrals, editorial typography, restrained motion, clear source cards, and a simple question-first experience.

## Included

- responsive landing/query experience
- live PolicyIQ readiness indicator
- real `POST /api/v1/query` integration
- example question cards
- loading state for long reranking requests
- answer rendering with bold text and clickable source references
- source cards with document ID + PDF page
- explicit abstention UI
- error state + retry
- expandable timing details
- mobile layout
- no UI kit, icon library, or Tailwind dependency

## Run locally

Keep the PolicyIQ backend running at:

```text
http://127.0.0.1:8000
```

Then:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The Vite dev server proxies `/api`, `/health`, and `/ready` to FastAPI, so you do not need to change backend CORS for local development.

## Build

```powershell
npm run build
```

Output is created in `dist/`.

## Future deployment

For a future hosted deployment you can set:

```env
VITE_API_BASE_URL=https://your-api.example.com
```

If frontend and backend use different origins, FastAPI must allow the frontend origin via CORS, or both services should sit behind one reverse proxy.
