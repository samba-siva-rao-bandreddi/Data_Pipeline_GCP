# Walkthrough — My Thinking Process

## How I Approached This Problem

Before jumping into solutions, I sat with the problem statement for a while. The team didn't say *"build us a dashboard."* They said *"help us figure out what to build."* That distinction matters — they wanted scoping, not engineering.

---

## Starting Point: Understanding the Real Problem

The surface-level problem is *"answering a question takes too long."* But the deeper problems are:

1. **Inconsistency** — Different analysts produce different answers. This erodes trust, both internally and with clients.
2. **Knowledge bottleneck** — The process lives in one person's head. When they are unavailable, the whole team is stuck.
3. **No single source of truth** — Data lives in 3–5 separate tools. The "answer" is constructed ad-hoc each time.

This told me the tool needs to prioritize **consistency and accessibility** over sophistication. A simple tool that gives the same answer every time is more valuable than a complex one that requires training.

---

## Who Is the User? (And Why It Changes Everything)

This was the first major design decision. The options were:

| User | Implications |
|---|---|
| **Internal analyst** | Simpler auth, less polish needed, can show raw metrics, internal jargon is fine |
| **Client** | Needs auth/permissions, white-labeling, careful about what data is exposed, higher design bar |
| **Both** | Two user experiences in one tool — significantly more complex |

**My decision: Internal analyst first.** Here is why:

- The problem statement explicitly says the *team* needs this. Clients are currently served through existing channels (emails, slide decks, calls).
- Building for clients in v1 introduces authentication, permissions, branding, and data sensitivity — each one is a project in itself.
- The analyst can still use the tool to *serve* clients faster. A screenshot or PDF export bridges the gap without building a client portal.
- If v1 proves valuable internally, extending it to clients becomes a v2 conversation backed by real usage data.

I considered the account manager as a secondary user — someone who is not an analyst but needs to answer *"how are things going?"* without waiting. The tool should be simple enough for them to self-serve.

---

## Defining "What Does Success Look Like?"

I imagined a concrete scenario:

> It is Monday morning. An account manager has a client call at 10 AM. They need to know how the client's marketing performed last week. Today, they would Slack the analyst, wait 30 minutes, and maybe get a partial answer.
>
> With the tool: They open it, select the client, see a cross-channel summary, notice that Google Ads ROAS improved but Meta spend is up with declining returns. They go into the call informed and confident. Total time: 90 seconds.

This scenario drove several design decisions:
- **Client selector** must be the first interaction (not buried in settings)
- **Default date range** should be "Last 7 days" (the most common ask)
- The view must be **scannable**, not a data dump — cards, not tables of raw numbers
- **Export** must be one click (the downstream action is always "share this with someone")

---

## What Data, and From Where?

The constraint is clear: *the team will not change their existing tools.* So the tool must integrate with whatever they already use. I assumed the standard martech stack:

- **Google Ads** — Paid search (almost every marketing team uses this)
- **Meta Ads** — Paid social (Facebook/Instagram)
- **An email platform** — Mailchimp, SendGrid, or HubSpot
- **Google Analytics 4** — Website analytics
- **Google Search Console** — Organic search performance

All of these have well-documented APIs. The integration strategy:
- **Adapters, not a monolith** — One Python script per source, each mapping to a common schema. This means adding a new source later is just writing a new adapter, not refactoring the whole system.
- **Daily batch, not real-time** — Marketing decisions are not made in real-time. Daily freshness is sufficient and dramatically simpler to build.
- **Pull, not push** — We fetch data from APIs on our schedule, rather than setting up webhooks. Simpler and more reliable for v1.

### The Hardest Part: Metric Normalization

Different platforms define the same concept differently:
- Google Ads "conversions" vs. Meta "actions" vs. email "clicks"
- Attribution windows vary across platforms
- Some channels (organic, email) don't have "spend"

**My call:** In v1, use each platform's native definition and label them clearly. Do not try to normalize attribution models — that is a rabbit hole. If Google says 45 conversions and Meta says 155, show both. The analyst knows how to interpret this. Trying to create a unified "truth" across platforms is premature and potentially misleading.

---

## Scoping v1: The Art of Leaving Things Out

This is where most tools fail — they try to do too much in v1 and either never ship or ship something half-baked.

My scoping principle: **v1 must answer exactly one question well.** That question is *"How is our marketing performing across channels right now, and where should we focus?"*

Everything that does not directly serve that question is v2.

### What I Included and Why

- **Cross-channel summary** — The core answer. Without this, the tool has no purpose.
- **Channel comparison** — Directly answers *"where should we focus?"* by showing relative performance.
- **Date range selector** — *"Right now"* means different things to different people. Last 7 days is the default but flexibility is needed.
- **Sparklines** — A number without context is dangerous. Conversions at 45 — is that good or bad? A sparkline showing a downward trend adds crucial context without adding complexity.
- **Data freshness indicator** — Trust killer #1 is stale data shown as current. Always show when data was last updated.
- **Export** — The most common action after viewing is sharing. One-click PDF export covers client emails, Slack messages, and meeting prep.

### What I Excluded and Why

**AI recommendations** — *"Shift budget from Meta to Google."* Sounds impressive, but:
- The team needs to trust the *data* before trusting *automated advice*
- Recommendation quality requires months of historical data to calibrate
- A bad recommendation erodes trust faster than no recommendation

**Custom report builder** — This is essentially building Looker/Data Studio. It is a product category, not a feature. If an analyst needs custom analysis, they use the tools they already have.

**Client-facing portal** — Auth + permissions + branding + data sensitivity = 4 separate projects. An analyst can screenshot the internal dashboard and email it. Solving the internal problem first is the priority.

**Campaign-level drill-down** — Going from channel → campaign → ad group → ad creates a tool that competes with the native platforms. Those tools will always be better at their own drill-downs. Stay at the channel level.

**Anomaly detection / alerts** — Useful in theory, but:
- You need to define "normal" before you can detect "anomalous"
- False positives create alert fatigue
- v1 needs usage data to establish baselines

---

## Architecture Decisions

### Why Not Just Use Google Data Studio / Looker?

Fair question. Reasons:

1. **The team cannot change their tools** — if they already had a centralized BI tool that did this, they would not have this problem
2. **Data Studio requires manual connector setup per client** — does not scale well for a multi-client agency
3. **Custom tools can encode team-specific logic** — the "channel comparison" view with the specific metrics this team cares about
4. **Ownership** — they can evolve it without depending on a third-party platform's roadmap

### Why a Database Instead of Just Querying APIs Directly?

- **Speed** — API calls take seconds; database queries take milliseconds
- **Reliability** — If Meta's API is down at 2 PM, you still have this morning's data
- **History** — APIs only return current/recent data. A database accumulates history over time
- **Cost** — API calls often have rate limits and quotas. Pulling once per day and caching is efficient

### Why SQLite for v1?

- Zero configuration, no server to manage
- Single file — easy to back up, move, or reset
- Good enough for the data volume (5 clients × 5 channels × 365 days = ~9,000 rows/year)
- Upgrade to PostgreSQL when needed, with minimal code changes

---

## What I Would Revisit With More Time

1. **User research** — I made assumptions about the team's workflow. Ideally, I would shadow an analyst through their current process to validate my assumptions about pain points and interaction patterns.

2. **Data source audit** — I assumed a standard martech stack. The actual tools and their API capabilities would shape the ingestion layer significantly.

3. **Metric definitions workshop** — Sit with the team to define *exactly* what "conversions" and "ROAS" mean per client and per channel. This alignment is critical for trust.

4. **Prototype testing** — Build a clickable prototype and put it in front of 2–3 analysts. Watch them use it. Their confusion and questions would reveal design flaws faster than any amount of planning.

5. **Client feedback loop** — Even though clients are not v1 users, understanding what information they actually want (vs. what the team assumes they want) would sharpen the tool's focus.

6. **Error handling depth** — What happens when a client has no data for a channel? When an API key expires? When the ingestion job fails silently? These edge cases need detailed design.

---

## Final Reflection

The biggest trap in this kind of problem is building for sophistication when the need is for simplicity. The team does not need an AI-powered marketing intelligence platform. They need a tool that lets anyone on the team answer a common question in 2 minutes instead of 45.

The best v1 is one that the team actually uses every day — not one that looks impressive in a demo but sits idle because it is too complex or too fragile. Start simple, build trust through accuracy and reliability, and let the users tell you what v2 should be.
