# Product Brief — Marketing Performance Hub (MPH)

## Problem

The team repeatedly gets asked: *"How is our marketing performing across channels, and where should we focus?"*

Answering this today is **manual** (30–60 min), **inconsistent** (varies by analyst), and **fragile** (depends on one person being available).

The data already exists in the tools — the problem is assembling it into a single, consistent answer.

---

## Who Is It For?

- **Primary:** Internal analysts/strategists who field performance questions daily
- **Secondary:** Account managers who need quick answers before client calls
- **Not in v1:** Clients (they receive exported summaries via email/Slack)

---

## What Does It Do? (v1)

A simple internal dashboard where a user can:

1. **Select a client** from a dropdown
2. **See a cross-channel summary** — spend, clicks, conversions, ROAS per channel
3. **Compare channels** — which one is performing best relative to spend
4. **Filter by date range** — last 7 days, 30 days, or custom
5. **Export** — one-click PDF for sharing with clients or in Slack

---

## Where Does the Data Come From?

Pulls from the team's **existing tools** via APIs (no tool changes required):

| Source | Data |
|---|---|
| Google Ads API | Paid search metrics |
| Meta Marketing API | Paid social metrics |
| Email platform API | Email campaign metrics |
| GA4 / Search Console | Organic & website analytics |

**Refresh:** Daily batch pull at 5 AM (not real-time — daily is enough for marketing decisions).

---

## What's NOT in v1?

| Excluded | Why |
|---|---|
| Client-facing portal | Adds auth, permissions, branding — too much scope |
| AI recommendations | Need to trust data first before trusting advice |
| Campaign-level drill-down | Native tools (Google Ads UI, Meta) do this better |
| Custom report builder | That's a whole product (Looker/Data Studio), not a feature |
| Real-time data | Daily is sufficient; real-time adds unnecessary complexity |

---

## How Do We Know It Worked?

| Metric | Target |
|---|---|
| Time to answer | < 2 min (down from 30–60 min) |
| Adoption | 80%+ of team uses it weekly within 1 month |
| Accuracy | Numbers match source platforms |

---

## What's Next (v2+)

- Period-over-period comparison (this week vs. last week)
- Anomaly alerts via Slack
- Campaign-level drill-down
- Client-facing read-only view
- AI-generated natural language summaries
