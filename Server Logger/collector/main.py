import os, logging, json
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import asyncpg
import asyncio

API_KEY = os.getenv("INGEST_API_KEY")
PG_DSN = os.getenv("PG_DSN", "postgres://postgres:dev@db:5432/commlogs")

app = FastAPI(title="Commlogs Collector", version="0.1.0")
pool = None
logger = logging.getLogger("collector")
logging.basicConfig(level=logging.INFO)

class LogEvent(BaseModel):
    ts: datetime
    source_host: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    latency_ms: Optional[int] = None
    bytes_in: Optional[int] = None
    bytes_out: Optional[int] = None
    service: Optional[str] = None
    raw: Optional[str] = None
    tags: Optional[dict] = None

@app.on_event("startup")
async def startup():
    global pool
    await asyncio.sleep(5)
    pool = await asyncpg.create_pool(dsn=PG_DSN, min_size=2, max_size=10)
    logger.info("DB pool created")

def validate_api_key(key: Optional[str]):
    if not key or (API_KEY is not None and key != API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized")

async def insert_batch(records):
    q = """INSERT INTO logs
        (ts, source_host, src_ip, dst_ip, src_port, dst_port, protocol, direction, status, latency_ms, bytes_in, bytes_out, service, raw, tags)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)"""
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(q, records)

def transform_event(e: LogEvent):
    return (e.ts, e.source_host, e.src_ip, e.dst_ip, e.src_port, e.dst_port,
            e.protocol, e.direction, e.status, e.latency_ms, e.bytes_in, e.bytes_out,
            e.service, e.raw, json.dumps(e.tags or {}))

@app.get("/health")
async def health():
    async with pool.acquire() as conn:
        await conn.execute("SELECT 1;")
    return {"ok": True}

@app.post("/ingest")
async def ingest(events: List[LogEvent], x_api_key: Optional[str] = Header(None), background_tasks: BackgroundTasks = None):
    validate_api_key(x_api_key)
    if len(events) == 0:
        return {"ok": True, "ingested": 0}
    if len(events) > 2000:
        raise HTTPException(status_code=413, detail="Batch too large")
    records = [transform_event(e) for e in events]
    background_tasks.add_task(insert_batch, records)
    return {"ok": True, "ingested": len(records)}

#backend code for our VOLUME metric
@app.get("/metrics/volume")
async def metrics_volume(
    bucket: str = Query("minute", regex="^(minute|hour|day)$"),
    minutes: int = Query(60, ge=1, le=24*60)
):
    #define our time window
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes = minutes)
    #querry in SQL
    sql = """
    SELECT date_trunc($1, ts) AS bucket, count(*) AS logs
    FROM logs
    WHERE ts BETWEEN $2 AND $3
    GROUP BY 1
    ORDER BY 1;    
    """
    #aquire our database conneciton from the pool and querry
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, bucket, start, end)
    #return ISO timestamps, frontend format HH:MM
    data = [{"bucket": r["bucket"].isoformat(), "logs": r["logs"]} for r in rows]
    return {"data": data}

#backend code for our ERROR metric
@app.get("/metrics/error")
async def metrics_error(
    minutes: int = Query(24 * 60, ge=1, le=7 * 24 * 60)
):
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)
    sql = """
    SELECT
      count(*) AS total,
      sum(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS errors
    FROM logs
    WHERE ts BETWEEN $1 AND $2;
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, start, end)
    total = row["total"] or 0
    errors = row["errors"] or 0
    error_pct = (errors / total * 100) if total else 0.0
    return {"total": total, "errors": errors, "error_pct": error_pct}

@app.get("/metrics/top-src")
async def metrics_top_src(
    minutes: int = Query(60, ge=1, le=24 * 60),
    limit: int = Query(10, ge=1, le=100)
):
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)
    sql = """
    SELECT
      COALESCE(src_ip::text, source_host) AS src,
      count(*) AS c
    FROM logs
    WHERE ts BETWEEN $1 AND $2
    GROUP BY 1
    ORDER BY c DESC
    LIMIT $3;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, start, end, limit)
    data = [{"src_ip": r["src"], "c": r["c"]} for r in rows]
    return {"rows": data}
