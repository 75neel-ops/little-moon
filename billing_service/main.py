from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Little Moon Billing")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])

DEFAULT_PLANS = [
    {"id": "15-days", "label": "15 days", "amount_rupees": 50, "duration_days": 15},
    {"id": "30-days", "label": "30 days", "amount_rupees": 100, "duration_days": 30},
    {"id": "3-months", "label": "3 months", "amount_rupees": 250, "duration_days": 90},
    {"id": "6-months", "label": "6 months", "amount_rupees": 450, "duration_days": 180},
    {"id": "1-year", "label": "1 year", "amount_rupees": 800, "duration_days": 365},
]


def configured_plans() -> list[dict[str, Any]]:
    raw = os.getenv("PLAN_CONFIG_JSON", "").strip()
    if not raw:
        return DEFAULT_PLANS
    import json
    try:
        plans = json.loads(raw)
        if not isinstance(plans, list) or not plans:
            raise ValueError
        for plan in plans:
            if not all(key in plan for key in ("id", "label", "amount_rupees", "duration_days")) or int(plan["amount_rupees"]) < 1 or int(plan["duration_days"]) < 1:
                raise ValueError
        return plans
    except (ValueError, TypeError, KeyError):
        raise HTTPException(503, "PLAN_CONFIG_JSON must be a valid list of plan objects.")


def env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise HTTPException(503, f"Billing is not configured: {name} is missing.")
    return value


def db_request(method: str, table: str, *, params: dict[str, str] | None = None, body: Any = None, prefer: str = "") -> Any:
    base = env("SUPABASE_URL").rstrip("/")
    service = env("SUPABASE_SERVICE_ROLE_KEY")
    headers = {"apikey": service, "Authorization": f"Bearer {service}", "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    response = requests.request(method, f"{base}/rest/v1/{table}", params=params, json=body, headers=headers, timeout=20)
    if not response.ok:
        raise HTTPException(502, "The access database request failed.")
    return response.json() if response.content else None


def current_user(authorization: str) -> dict[str, Any]:
    token = authorization.removeprefix("Bearer ").strip()
    if not token or token == authorization:
        raise HTTPException(401, "Please sign in again.")
    response = requests.get(f"{env('SUPABASE_URL').rstrip('/')}/auth/v1/user", headers={"apikey": env("SUPABASE_ANON_KEY"), "Authorization": f"Bearer {token}"}, timeout=15)
    if not response.ok:
        raise HTTPException(401, "Your sign-in expired. Please sign in again.")
    return response.json()


def ensure_profile(user: dict[str, Any]) -> dict[str, Any]:
    uid = user["id"]
    existing = db_request("GET", "lm_profiles", params={"user_id": f"eq.{uid}", "select": "*", "limit": "1"})
    if existing:
        return existing[0]
    try:
        created = db_request("POST", "lm_profiles", body={"user_id": uid, "email": user.get("email", "")}, prefer="return=representation")
        return created[0]
    except HTTPException:
        # Concurrent first sign-ins can race on the unique user_id. Re-read the winner.
        existing = db_request("GET", "lm_profiles", params={"user_id": f"eq.{uid}", "select": "*", "limit": "1"})
        if existing:
            return existing[0]
        raise


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class PlanRequest(BaseModel):
    plan_id: str


class PaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/plans")
def plans() -> dict[str, Any]:
    return {"plans": [{**p, "amount_paise": p["amount_rupees"] * 100} for p in configured_plans()]}


@app.get("/entitlement")
def entitlement(authorization: str = Header(default="")) -> dict[str, Any]:
    user = current_user(authorization)
    profile = ensure_profile(user)
    now = datetime.now(timezone.utc)
    paid_until = parse_date(profile.get("access_expires_at"))
    if paid_until and paid_until > now:
        return {"active": True, "trial": False, "label": profile.get("plan_label") or "Paid access", "expires_at": paid_until.isoformat()}
    trial_end = parse_date(profile["trial_started_at"]) + timedelta(days=2)
    if now < trial_end:
        return {"active": True, "trial": True, "label": "Free trial", "expires_at": trial_end.isoformat()}
    return {"active": False, "trial": True, "expires_at": trial_end.isoformat(), "message": "Sign in with the same email you used to start your trial."}


@app.post("/create-order")
def create_order(data: PlanRequest, authorization: str = Header(default="")) -> dict[str, Any]:
    user = current_user(authorization)
    ensure_profile(user)
    plan = next((item for item in configured_plans() if item["id"] == data.plan_id), None)
    if not plan:
        raise HTTPException(404, "That plan is not available.")
    key_id = env("RAZORPAY_KEY_ID")
    key_secret = env("RAZORPAY_KEY_SECRET")
    response = requests.post("https://api.razorpay.com/v1/orders", auth=(key_id, key_secret), json={"amount": plan["amount_rupees"] * 100, "currency": "INR", "receipt": f"lm-{user['id'][:8]}-{plan['id']}", "notes": {"user_id": user["id"], "plan_id": plan["id"]}}, timeout=20)
    if not response.ok:
        raise HTTPException(502, "Razorpay could not create the order. Please retry.")
    order = response.json()
    db_request("POST", "lm_orders", body={"order_id": order["id"], "user_id": user["id"], "plan_id": plan["id"], "plan_label": plan["label"], "amount_paise": plan["amount_rupees"] * 100, "duration_days": plan["duration_days"]}, prefer="return=minimal")
    return {"order_id": order["id"], "amount_paise": order["amount"], "key_id": key_id}


@app.post("/verify-payment")
def verify_payment(data: PaymentRequest, authorization: str = Header(default="")) -> dict[str, Any]:
    user = current_user(authorization)
    orders = db_request("GET", "lm_orders", params={"order_id": f"eq.{data.razorpay_order_id}", "user_id": f"eq.{user['id']}", "select": "*", "limit": "1"})
    if not orders:
        raise HTTPException(404, "This payment order does not belong to your account.")
    order = orders[0]
    expected = hmac.new(env("RAZORPAY_KEY_SECRET").encode(), f"{order['order_id']}|{data.razorpay_payment_id}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, data.razorpay_signature):
        raise HTTPException(400, "Payment signature could not be verified.")
    payment_response = requests.get(f"https://api.razorpay.com/v1/payments/{data.razorpay_payment_id}", auth=(env("RAZORPAY_KEY_ID"), env("RAZORPAY_KEY_SECRET")), timeout=20)
    if not payment_response.ok:
        raise HTTPException(502, "Could not confirm payment status with Razorpay.")
    payment = payment_response.json()
    if payment.get("order_id") != order["order_id"] or payment.get("amount") != order["amount_paise"] or payment.get("currency") != "INR" or payment.get("status") != "captured":
        raise HTTPException(400, "Razorpay has not confirmed a captured payment for this order yet.")
    db_request("POST", "rpc/complete_lm_payment", body={"p_order_id": order["order_id"], "p_payment_id": data.razorpay_payment_id})
    return {"verified": True, "message": "Payment verified. Your Little Moon access is active."}

