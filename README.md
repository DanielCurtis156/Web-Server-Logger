Server Logger

This is a  **server communications logging app**. It includes:

- **collector/** — FastAPI ingestion service (`POST /ingest`) with API key auth and batched inserts
- **db/** — PostgreSQL init scripts (schema + indexes). Optional TimescaleDB step documented
- **ui/** — Next.js dashboard
- **vector/** — Example Vector agent config to ship real logs to the collector
- **scripts/** — Local traffic generator to push sample events into the collector
- **docker-compose.yml** — One command dev stack (Postgres + Collector + UI)
- **.env.example** —

## Quickstart

```bash
# 1) Copy env and edit the values (if needed)
cp .env.example .env

# 2) Build and start
docker compose up --build

# 3) Seed some sample events (in another terminal)
python3 scripts/seed.py

# 4) Open the UI
#    http://localhost:3000
#    Collector is at http://localhost:8080 (POST /ingest)
```

> Default API key: `secret123`

---

## What’s Included and How It Fits

### 1) **Collector (FastAPI)**
- Exposes `POST /ingest` for **batched JSON** events from agents (Vector/Fluent Bit) or your apps.
- Validates an **`X-API-KEY`** header before accepting data.
- Performs **batched inserts** into Postgres using `asyncpg`.
- Designed to be **low-latency**: acknowledges quickly; writes in a background task.
- Extend `transform_event()` for **redaction** or normalization and add enrichment workers later.

### 2) **Database (Postgres)**
- Schema captures typical comm-log fields: timestamps, IPs/ports, protocol, service, status, bytes, latency, raw, tags (JSONB).
- Helpful indexes are created for time, status, service, IP, and port.
- Production tips:
  - Consider **TimescaleDB hypertables** for heavy time-series.
  - Use **partitioning** or **ClickHouse** later for massive volumes.

### 3) **UI (Next.js)**
- Minimal dashboard with:
  - Volume over time
  - Error rate KPI
  - Top source IPs table
- The UI hits the **collector’s simple metrics endpoints** (provided here as mock routes). You can point it at real endpoints once you add them to the collector (see TODOs).
- Uses **Recharts** and **Tailwind**; clean layout ready to extend (search page, filters, saved queries).

### 4) **Vector Agent (example)**
- A sample `vector.toml` shows how to:
  - Tail an nginx access log (or any file), parse it, add `source_host`, then
  - **POST batches as JSON** to `https://your-collector/ingest` with `X-API-KEY` header.
- Vector handles buffering/retries so you don’t lose logs during outages.

### 5) **Scripts**
- `seed.py` generates realistic events and sends them to your collector for **smoke tests**.
- Great for verifying your dashboard updates in real time.

---

## Roadmap (after MVP)

- Add `/metrics/*` endpoints to collector for:
  - Logs per minute (time range)
  - Error rate
  - Top IPs / ports / services
  - Latency percentiles
- Wire UI charts to those endpoints (currently mocked).
- Add **auth** to the UI (JWT/OIDC) and RBAC.
- Add **GeoIP/ASN** enrichment and threat feed tagging.
- Switch DB to **ClickHouse** when volume grows.
- Optional **Kafka** between collector and DB for burst tolerance.

---

## Endpoints

### Collector
- `POST /ingest` — Accepts a JSON array of events (see schema in `collector/main.py`).
  - Requires `X-API-KEY` header.

### UI (dev)
- `GET /api/mock/metrics/*` — Mock APIs for charts; replace with real collector endpoints when ready.

---

## Environment Variables

From `.env.example`:
- `PG_DSN` — Postgres connection string used by the collector
- `INGEST_API_KEY` — Shared secret expected in `X-API-KEY` header
- `UI_API_BASE` — Base URL where the UI calls APIs (defaults to local dev)

---

## Security Notes

- Rotate API keys; prefer **mTLS** per host if you control the fleet.
- Enforce TLS at the edge (Caddy/Nginx/Traefik) and size limits on requests.
- Redact PII and secrets in `raw` at the agent or collector.
- Add audit logging and per-source rate limits.
