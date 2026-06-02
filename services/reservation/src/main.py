import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Literal, Optional

from fastapi import FastAPI, Header, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field


SERVICE_NAME = os.getenv("SERVICE_NAME", "reservation-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)

REQUEST_COUNT = Counter(
    "nekocafe_http_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)
REQUEST_DURATION = Histogram(
    "nekocafe_http_request_duration_seconds",
    "HTTP request duration",
    ["service", "method", "path"],
)


class ReservationCreate(BaseModel):
    member_id: str = Field(..., examples=["m001"])
    store_id: str = Field(..., examples=["store-bj-001"])
    table_id: str = Field(..., examples=["t08"])
    reserved_at: str = Field(..., examples=["2026-06-05T18:30:00+08:00"])
    party_size: int = Field(..., ge=1, le=8, examples=[2])
    special_request: Optional[str] = Field(default="", examples=["靠窗，低糖甜品"])


class Reservation(BaseModel):
    id: str
    member_id: str
    store_id: str
    table_id: str
    reserved_at: str
    party_size: int
    status: Literal["CONFIRMED", "CHECKED_IN", "CANCELLED"]
    special_request: str = ""
    created_at: str


RESERVATIONS: Dict[str, Reservation] = {}

app = FastAPI(
    title="NekoCafe Reservation Service",
    version=SERVICE_VERSION,
    description="PoC service for reservation and queue bounded context.",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_log(level: str, message: str, trace_id: str, **fields) -> None:
    record = {
        "timestamp": utc_now(),
        "level": level,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "traceId": trace_id,
        "message": message,
        **fields,
    }
    logger.info(json.dumps(record, ensure_ascii=False))


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    started = time.time()
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    response: Response
    try:
        response = await call_next(request)
    except Exception as exc:
        write_log("error", "request failed", trace_id, path=request.url.path, error=str(exc))
        raise
    finally:
        duration = time.time() - started
    path = request.url.path
    status = str(response.status_code)
    REQUEST_COUNT.labels(SERVICE_NAME, request.method, path, status).inc()
    REQUEST_DURATION.labels(SERVICE_NAME, request.method, path).observe(duration)
    response.headers["x-trace-id"] = trace_id
    write_log(
        "info",
        "request completed",
        trace_id,
        method=request.method,
        path=path,
        status=response.status_code,
        latency_ms=round(duration * 1000, 2),
    )
    return response


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readyz():
    return {"status": "ready", "dependencies": {"database": "mock", "redis": "mock"}}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/reservations", response_model=Reservation, status_code=201)
def create_reservation(payload: ReservationCreate, x_trace_id: Optional[str] = Header(default=None)):
    trace_id = x_trace_id or str(uuid.uuid4())
    reservation_id = f"rsv_{uuid.uuid4().hex[:10]}"
    reservation = Reservation(
        id=reservation_id,
        member_id=payload.member_id,
        store_id=payload.store_id,
        table_id=payload.table_id,
        reserved_at=payload.reserved_at,
        party_size=payload.party_size,
        status="CONFIRMED",
        special_request=payload.special_request or "",
        created_at=utc_now(),
    )
    RESERVATIONS[reservation_id] = reservation
    write_log("info", "reservation created", trace_id, reservationId=reservation_id, storeId=payload.store_id)
    return reservation


@app.get("/reservations/{reservation_id}", response_model=Reservation)
def get_reservation(reservation_id: str):
    reservation = RESERVATIONS.get(reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="reservation not found")
    return reservation


@app.post("/reservations/{reservation_id}/checkin", response_model=Reservation)
def checkin_reservation(reservation_id: str, x_trace_id: Optional[str] = Header(default=None)):
    reservation = RESERVATIONS.get(reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="reservation not found")
    if reservation.status == "CANCELLED":
        raise HTTPException(status_code=409, detail="cancelled reservation cannot check in")
    updated = reservation.model_copy(update={"status": "CHECKED_IN"})
    RESERVATIONS[reservation_id] = updated
    write_log("info", "reservation checked in", x_trace_id or str(uuid.uuid4()), reservationId=reservation_id)
    return updated


@app.delete("/reservations/{reservation_id}", response_model=Reservation)
def cancel_reservation(reservation_id: str):
    reservation = RESERVATIONS.get(reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="reservation not found")
    if reservation.status == "CHECKED_IN":
        raise HTTPException(status_code=409, detail="checked-in reservation cannot be cancelled")
    updated = reservation.model_copy(update={"status": "CANCELLED"})
    RESERVATIONS[reservation_id] = updated
    return updated
