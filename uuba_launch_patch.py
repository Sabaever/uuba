#!/usr/bin/env python3
from pathlib import Path

ROOT = Path('/app')
APP = ROOT / 'app.py'
CASE = ROOT / 'case-review.html'
CASEWORK = ROOT / 'caseworker-admin.html'
MARKER = '# UUBA LAUNCH INTAKE V3'

API = r'''
# UUBA LAUNCH INTAKE V3
import os as _uo, re as _ur, secrets as _us
from datetime import datetime as _ud, timezone as _utz
from fastapi import Request as _Req, HTTPException as _HTTP
from sqlalchemy import create_engine as _ce, text as _sql

_db = _uo.getenv("DATABASE_URL", "").strip()
if _db.startswith("postgres://"):
    _db = "postgresql://" + _db[len("postgres://"):]
_eng = _ce(_db, pool_pre_ping=True) if _db else None
_STATUSES = {"new","triage","awaiting_information","scoped","quoted","accepted","payment_pending","in_review","qa","completed","declined"}

def _init():
    if _eng is None:
        raise _HTTP(503, "Case review storage is not configured")
    ddl = """CREATE TABLE IF NOT EXISTS uuba_case_intake(
      id BIGSERIAL PRIMARY KEY,
      reference VARCHAR(32) UNIQUE NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      customer_name VARCHAR(200) NOT NULL,
      email VARCHAR(320) NOT NULL,
      phone VARCHAR(80),
      category VARCHAR(120) NOT NULL,
      trader_name VARCHAR(240),
      amount_in_dispute VARCHAR(120),
      deadline VARCHAR(120),
      summary TEXT NOT NULL,
      desired_outcome TEXT,
      evidence_notes TEXT,
      has_documents BOOLEAN NOT NULL DEFAULT FALSE,
      privacy_consent BOOLEAN NOT NULL DEFAULT FALSE,
      status VARCHAR(40) NOT NULL DEFAULT 'new',
      scope_level VARCHAR(60),
      quote_amount NUMERIC(10,2),
      quote_notes TEXT,
      payment_reference VARCHAR(240),
      internal_notes TEXT,
      assigned_to VARCHAR(160),
      reviewed_at TIMESTAMPTZ,
      closed_at TIMESTAMPTZ)"""
    with _eng.begin() as c:
        c.execute(_sql(ddl))
        c.execute(_sql("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_status ON uuba_case_intake(status)"))
        c.execute(_sql("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_created ON uuba_case_intake(created_at DESC)"))

def _admin(request):
    expected = _uo.getenv("UUBA_ADMIN_TOKEN", "")
    auth = request.headers.get("authorization", "")
    supplied = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    if not expected or not _us.compare_digest(supplied, expected):
        raise _HTTP(401, "Admin access was not accepted")

def _clean(v, n=4000):
    if v is None: return None
    v = str(v).replace(chr(0), "").strip()
    return v[:n] if v else None

def _row(r):
    d = dict(r._mapping)
    for k,v in list(d.items()):
        if hasattr(v, "isoformat"): d[k] = v.isoformat()
        elif k == "quote_amount" and v is not None: d[k] = float(v)
    return d

@app.post("/api/case-review/intake")
async def uuba_case_review_intake(request:_Req):
    _init()
    try: d = await request.json()
    except Exception: raise _HTTP(400, "Invalid request")
    if _clean(d.get("website"), 200):
        return {"ok": True, "reference": "UUBA-REVIEW"}
    name = _clean(d.get("name"),200); email = _clean(d.get("email"),320)
    category = _clean(d.get("category"),120); summary = _clean(d.get("summary"),8000)
    if not all((name,email,category,summary)):
        raise _HTTP(400, "Name, email, category and case summary are required")
    if not _ur.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise _HTTP(400, "Enter a valid email address")
    if len(summary) < 40:
        raise _HTTP(400, "Please provide a little more detail about the dispute")
    if not bool(d.get("privacy_consent")):
        raise _HTTP(400, "You must confirm the review-request terms")
    ref = "UUBA-CR-" + _ud.now(_utz.utc).strftime("%Y%m%d") + "-" + _us.token_hex(3).upper()
    q = _sql("""INSERT INTO uuba_case_intake(reference,customer_name,email,phone,category,trader_name,amount_in_dispute,deadline,summary,desired_outcome,evidence_notes,has_documents,privacy_consent,status)
    VALUES(:reference,:customer_name,:email,:phone,:category,:trader_name,:amount_in_dispute,:deadline,:summary,:desired_outcome,:evidence_notes,:has_documents,TRUE,'new') RETURNING reference""")
    p = {"reference":ref,"customer_name":name,"email":email.lower(),"phone":_clean(d.get("phone"),80),"category":category,"trader_name":_clean(d.get("trader_name"),240),"amount_in_dispute":_clean(d.get("amount_in_dispute"),120),"deadline":_clean(d.get("deadline"),120),"summary":summary,"desired_outcome":_clean(d.get("desired_outcome"),5000),"evidence_notes":_clean(d.get("evidence_notes"),5000),"has_documents":bool(d.get("has_documents"))}
