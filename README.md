# UAE MSP Lead Agent (Autonomous FastAPI Service)

A production-style, autonomous lead-generation agent focused on **publicly available UAE MSP / IT support / outsourcing / hiring signals**.

## Overview

This project is not a simple CRUD app: it runs a daily autonomous pipeline that discovers candidate companies/pages, inspects evidence, reasons about lead quality, deduplicates, stores qualified leads, and generates a daily report.

## Compliance & Guardrails

- Only collect **public business contact data**.
- Do **not** scrape private/personal data.
- Do **not** bypass authentication, anti-bot protections, or access controls.
- Respect `robots.txt`, website terms, and applicable privacy/marketing laws.
- Keep integrations conservative and auditable.

## Architecture

1. **Discovery (`app/services/discovery.py`)**
   - Query intent covers UAE MSP, managed IT, IT support/helpdesk, outsourcing, Microsoft 365 support, and IT hiring.
   - Uses `MockDiscoveryProvider` by default for reliable local/dev behavior.
   - Includes a pluggable `DiscoveryProvider` abstraction and `HttpDiscoveryProvider` scaffold for future live integrations.

2. **Parsing (`app/services/parser.py`)**
   - Extracts emails, phone numbers, links, careers/contact pages, UAE city mentions, and service keywords.

3. **Reasoning (`app/agent/reasoner.py`)**
   - Rule-based "thinking" layer evaluates evidence and returns:
     - classification
     - confidence score
     - save decision
     - explanation
     - detected signals

4. **Deduplication (`app/services/dedup.py`)**
   - Primary dedup key: website
   - Secondary dedup key: company name

5. **Storage & Reporting (`app/services/storage.py`, `app/services/reporting.py`)**
   - SQLite tables: `leads`, `run_logs`, `daily_reports`

6. **Agent Engine (`app/agent/engine.py`)**
   - End-to-end autonomous cycle orchestration.

7. **Scheduler (`app/agent/scheduler.py`)**
   - APScheduler daily cron in UTC.
   - Starts automatically on app startup.

## Reasoning Pipeline

For each candidate:
1. Discover candidate page/company.
2. Parse and inspect public evidence.
3. Classify lead type (`MSP`, `IT Support Provider`, `Hiring Lead`, `Outsourcing Opportunity`, `Unknown`).
4. Score confidence.
5. Decide save/reject with explanation.
6. Deduplicate.
7. Save qualified leads and update daily report.


## Web GUI (Jinja2 Dashboard)

The app now includes a server-rendered admin dashboard with lightweight CSS.

### GUI Routes

- `GET /` → dashboard with scheduler status, run timing, today lead counts, report summary, and manual run button
- `POST /run-agent-ui` → triggers one agent cycle and redirects back to dashboard
- `GET /runs` → run log table
- `GET /leads-ui` → saved leads table

### Manual Run Workflow

1. Open `/` in your browser.
2. Click **Run Agent Now**.
3. You are redirected back with a success/failure banner.
4. Review `/runs` and `/leads-ui` for outcomes.

## API Endpoints

- `GET /health` → `{ "status": "ok" }`
- `GET /leads` → list leads
- `GET /leads/{lead_id}` → one lead
- `DELETE /leads/{lead_id}` → delete lead
- `POST /run-agent` → trigger one full autonomous cycle
- `GET /reports/daily` → latest daily report
- `GET /agent/status` → last run, next run, today counts, latest result

## Local Setup

### Requirements
- Python 3.11

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Run

```bash
uvicorn app.main:app --reload
```

### Test

```bash
pytest -q
```

## Environment Variables

- `APP_NAME`
- `ENVIRONMENT`
- `DATABASE_PATH`
- `SCHEDULER_ENABLED` (`true/false`)
- `SCHEDULER_HOUR_UTC` (0-23)
- `SCHEDULER_MINUTE_UTC` (0-59)
- `REASONER_SAVE_THRESHOLD` (0.0-1.0)
- `DISCOVERY_MODE` (`mock` or `live` scaffold)

## How Daily Autonomous Runs Work

- On startup, app initializes DB and scheduler.
- APScheduler executes one daily cron job in UTC.
- Job runs full agent cycle:
  - discover candidates
  - parse evidence
  - reason/classify/score
  - deduplicate
  - save qualified leads
  - write run log + daily report

## Render Deployment

1. Push repo to GitHub.
2. Create a new Render Web Service from repo.
3. Render auto-detects `render.yaml`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Configure env vars if needed.

### Render scheduling note

On free/sleeping web tiers, precise job timing may drift or pause when instance sleeps. For reliable daily autonomy, use an always-on instance or trigger `/run-agent` via external cron.

## Phase 2 Roadmap

- Real search integration (public, compliant sources)
- LLM-based reasoning replacement for rule engine
- CRM export (HubSpot/Salesforce/CSV pipelines)
- Email/Slack notifications on new high-confidence leads
- Persistent production DB (PostgreSQL)

## Mock/Scaffolded Components (to replace for full production autonomy)

- `MockDiscoveryProvider` currently provides realistic sample candidates.
- `HttpDiscoveryProvider` is a safe scaffold with no paid APIs or bypass behavior.
- Rule-based reasoner is intentionally modular so a true LLM reasoner can be swapped in.
