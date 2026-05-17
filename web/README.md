# AgentMemoryCTF Web UI

Interactive live CTF frontend for attacking agent memory systems.

## Setup

```bash
npm install
```

## Running Locally

Start the Python API from the repository root:

```bash
source venv/bin/activate
uvicorn api.server:app --reload --port 8000
```

Start the frontend from `web/`:

```bash
npm run dev
```

Visit http://localhost:3000

By default the frontend calls `http://localhost:8000`. Override with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Structure

- `app/page.tsx` — Arena map with level cards
- `app/levels/[levelId]/page.tsx` — Challenge page
- `app/results/page.tsx` — Local score and attempt history
- `app/layout.tsx` — Global layout
- `components/` — Reusable UI components
- `lib/` — API client and local progress storage
- `public/` — Static assets

## Design

- **Language:** English
- **Mode:** Live targets only (`mem0`, `Hindsight`)
- **Progress:** Browser `localStorage`
- **Aesthetic:** Game-like CTF challenge map with dark panels and attack-family accents
- **Visibility:** Game-hidden results; raw snapshots and retrieved memories are not shown

## TODO

- [x] Create level pages (challenge pages for each L1–L5)
- [x] Add challenge submission UI
- [x] Wire up backend API calls
- [ ] Add leaderboard
- [ ] Add results visualization
- [ ] Add defense configuration UI
