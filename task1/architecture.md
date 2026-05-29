# Architecture — Marketing Performance Hub

## System Flow

![System Flow](wireframes/user_flow_diagram.png)


## How It Works

1. **Extract** — A daily cron job runs Python adapters that pull metrics from each platform's API
2. **Transform** — Each adapter normalizes platform-specific fields (e.g., Meta's `spend` → common `spend`, Google's `cost_micros / 1e6` → common `spend`) into a unified schema
3. **Load** — Normalized records are stored in a lightweight database (SQLite for v1)
4. **Serve** — A Python backend aggregates data by client + channel + date range and serves it as JSON
5. **Display** — The dashboard renders KPI cards, channel comparison, and export functionality

## Key Design Choices

| Decision | Reasoning |
|---|---|
| **Daily batch, not real-time** | Marketing decisions aren't real-time; daily refresh is sufficient and far simpler |
| **One adapter per source** | Adding a new platform = writing one new file, not refactoring the system |
| **SQLite for v1** | Zero-config, single file, easy backup — upgrade to PostgreSQL when needed |
| **Internal only** | No auth/permissions complexity — analysts export PDFs to share with clients |
