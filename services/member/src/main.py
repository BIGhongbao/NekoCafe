import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field


SERVICE_NAME = os.getenv("SERVICE_NAME", "member-service")
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


class Member(BaseModel):
    id: str
    nickname: str
    phone_masked: str
    level: str
    points: int
    coupons: int
    marketing_consent: bool


class Benefit(BaseModel):
    member_id: str
    level: str
    points: int
    coupons: int
    next_level_points: int


class ConsentUpdate(BaseModel):
    granted: bool = Field(..., examples=[True])


MEMBERS: Dict[str, Member] = {
    "m001": Member(
        id="m001",
        nickname="NekoFan",
        phone_masked="138****2703",
        level="Gold",
        points=1280,
        coupons=3,
        marketing_consent=True,
    ),
    "m002": Member(
        id="m002",
        nickname="LatteCat",
        phone_masked="139****6618",
        level="Silver",
        points=520,
        coupons=1,
        marketing_consent=False,
    ),
}

app = FastAPI(
    title="NekoCafe Member Service",
    version=SERVICE_VERSION,
    description="PoC service for member and benefit bounded context.",
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
    response = await call_next(request)
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
    return {"status": "ready", "dependencies": {"database": "mock"}}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/members/{member_id}", response_model=Member)
def get_member(member_id: str):
    member = MEMBERS.get(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    return member


@app.get("/members/{member_id}/benefits", response_model=Benefit)
def get_benefits(member_id: str):
    member = MEMBERS.get(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    return Benefit(
        member_id=member.id,
        level=member.level,
        points=member.points,
        coupons=member.coupons,
        next_level_points=max(0, 2000 - member.points),
    )


@app.post("/members/{member_id}/coupons/redeem", response_model=Benefit)
def redeem_coupon(member_id: str, x_trace_id: Optional[str] = Header(default=None)):
    member = MEMBERS.get(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    if member.coupons <= 0:
        raise HTTPException(status_code=409, detail="no coupons available")
    updated = member.model_copy(update={"coupons": member.coupons - 1})
    MEMBERS[member_id] = updated
    write_log("info", "coupon redeemed", x_trace_id or str(uuid.uuid4()), memberId=member_id)
    return get_benefits(member_id)


@app.put("/members/{member_id}/marketing-consent", response_model=Member)
def update_marketing_consent(member_id: str, payload: ConsentUpdate):
    member = MEMBERS.get(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="member not found")
    updated = member.model_copy(update={"marketing_consent": payload.granted})
    MEMBERS[member_id] = updated
    return updated
