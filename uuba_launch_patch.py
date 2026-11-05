#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

# Ensure runtime database dependencies are present in the built image.
subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "SQLAlchemy>=2,<3", "psycopg2-binary>=2.9,<3"])

ROOT = Path("/app")
APP = ROOT / "app.py"
CASE = ROOT / "case-review.html"
CASEWORK = ROOT / "caseworker-admin.html"
MARKER = "# UUBA LAUNCH INTAKE V4"

API = '\n# UUBA LAUNCH INTAKE V4\nimport os as _uo, re as _ur, secrets as _us\nfrom datetime import datetime as _ud, timezone as _utz\nfrom fastapi import Request as _Req, HTTPException as _HTTP\nfrom sqlalchemy import create_engine as _ce, text as _sql\n\n_db = _uo.getenv("DATABASE_URL", "").strip()\nif _db.startswith("postgres://"):\n    _db = "postgresql://" + _db[len("postgres://"):]\n_eng = _ce(_db, pool_pre_ping=True) if _db else None\n_STATUSES = {"new","triage","awaiting_information","scoped","quoted","accepted","payment_pending","in_review","qa","completed","declined"}\n\ndef _init():\n    if _eng is None:\n        raise _HTTP(503, "Case review storage is not configured")\n    ddl = """CREATE TABLE IF NOT EXISTS uuba_case_intake(\n      id BIGSERIAL PRIMARY KEY,\n      reference VARCHAR(32) UNIQUE NOT NULL,\n      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n      customer_name VARCHAR(200) NOT NULL,\n      email VARCHAR(320) NOT NULL,\n      phone VARCHAR(80),\n      category VARCHAR(120) NOT NULL,\n      trader_name VARCHAR(240),\n      amount_in_dispute VARCHAR(120),\n      deadline VARCHAR(120),\n      summary TEXT NOT NULL,\n      desired_outcome TEXT,\n      evidence_notes TEXT,\n      has_documents BOOLEAN NOT NULL DEFAULT FALSE,\n      privacy_consent BOOLEAN NOT NULL DEFAULT FALSE,\n      status VARCHAR(40) NOT NULL DEFAULT \'new\',\n      scope_level VARCHAR(60),\n      quote_amount NUMERIC(10,2),\n      quote_notes TEXT,\n      payment_reference VARCHAR(240),\n      internal_notes TEXT,\n      assigned_to VARCHAR(160),\n      reviewed_at TIMESTAMPTZ,\n      closed_at TIMESTAMPTZ)"""\n    with _eng.begin() as c:\n        c.execute(_sql(ddl))\n        c.execute(_sql("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_status ON uuba_case_intake(status)"))\n        c.execute(_sql("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_created ON uuba_case_intake(created_at DESC)"))\n\ndef _admin(request):\n    expected = _uo.getenv("UUBA_ADMIN_TOKEN", "")\n    auth = request.headers.get("authorization", "")\n    supplied = auth[7:].strip() if auth.lower().startswith("bearer ") else ""\n    if not expected or not _us.compare_digest(supplied, expected):\n        raise _HTTP(401, "Admin access was not accepted")\n\ndef _clean(v, n=4000):\n    if v is None:\n        return None\n    v = str(v).replace(chr(0), "").strip()\n    return v[:n] if v else None\n\ndef _row(r):\n    d = dict(r._mapping)\n    for k,v in list(d.items()):\n        if hasattr(v, "isoformat"):\n            d[k] = v.isoformat()\n        elif k == "quote_amount" and v is not None:\n            d[k] = float(v)\n    return d\n\n@app.post("/api/case-review/intake")\nasync def uuba_case_review_intake(request:_Req):\n    _init()\n    try:\n        d = await request.json()\n    except Exception:\n        raise _HTTP(400, "Invalid request")\n    if _clean(d.get("website"), 200):\n        return {"ok": True, "reference": "UUBA-REVIEW"}\n    name = _clean(d.get("name"),200)\n    email = _clean(d.get("email"),320)\n    category = _clean(d.get("category"),120)\n    summary = _clean(d.get("summary"),8000)\n    if not all((name,email,category,summary)):\n        raise _HTTP(400, "Name, email, category and case summary are required")\n    if not _ur.match(r"^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$", email):\n        raise _HTTP(400, "Enter a valid email address")\n    if len(summary) < 40:\n        raise _HTTP(400, "Please provide a little more detail about the dispute")\n    if not bool(d.get("privacy_consent")):\n        raise _HTTP(400, "You must confirm the review-request terms")\n    ref = "UUBA-CR-" + _ud.now(_utz.utc).strftime("%Y%m%d") + "-" + _us.token_hex(3).upper()\n    q = _sql("""INSERT INTO uuba_case_intake(reference,customer_name,email,phone,category,trader_name,amount_in_dispute,deadline,summary,desired_outcome,evidence_notes,has_documents,privacy_consent,status)\n    VALUES(:reference,:customer_name,:email,:phone,:category,:trader_name,:amount_in_dispute,:deadline,:summary,:desired_outcome,:evidence_notes,:has_documents,TRUE,\'new\') RETURNING reference""")\n    p = {\n        "reference":ref,\n        "customer_name":name,\n        "email":email.lower(),\n        "phone":_clean(d.get("phone"),80),\n        "category":category,\n        "trader_name":_clean(d.get("trader_name"),240),\n        "amount_in_dispute":_clean(d.get("amount_in_dispute"),120),\n        "deadline":_clean(d.get("deadline"),120),\n        "summary":summary,\n        "desired_outcome":_clean(d.get("desired_outcome"),5000),\n        "evidence_notes":_clean(d.get("evidence_notes"),5000),\n        "has_documents":bool(d.get("has_documents")),\n    }\n    with _eng.begin() as c:\n        r = c.execute(q,p).first()\n    return {"ok": True, "reference": r.reference, "message": "Received for initial scope assessment. Uúba has not yet accepted the case or started substantive work."}\n\n@app.get("/api/admin/case-intake")\ndef uuba_admin_case_intake(request:_Req, status:str="", limit:int=100):\n    _admin(request)\n    _init()\n    limit=max(1,min(limit,250))\n    p={"limit":limit}\n    where=""\n    if status:\n        if status not in _STATUSES:\n            raise _HTTP(400, "Invalid status")\n        where=" WHERE status=:status"\n        p["status"]=status\n    with _eng.begin() as c:\n        rows = c.execute(_sql("SELECT * FROM uuba_case_intake"+where+" ORDER BY created_at DESC LIMIT :limit"), p).fetchall()\n    return {"items": [_row(r) for r in rows], "count": len(rows)}\n\n@app.get("/api/admin/case-intake/summary")\ndef uuba_admin_case_intake_summary(request:_Req):\n    _admin(request)\n    _init()\n    with _eng.begin() as c:\n        rows = c.execute(_sql("SELECT status,COUNT(*) n FROM uuba_case_intake GROUP BY status")).fetchall()\n    n = {r.status:int(r.n) for r in rows}\n    out = {k:n.get(k,0) for k in _STATUSES}\n    out["new_requests"] = n.get("new",0)\n    out["active_reviews"] = sum(n.get(k,0) for k in ("accepted","payment_pending","in_review","qa"))\n    return out\n\n@app.get("/api/admin/case-intake/{reference}")\ndef uuba_admin_case_intake_detail(reference:str, request:_Req):\n    _admin(request)\n    _init()\n    with _eng.begin() as c:\n        r = c.execute(_sql("SELECT * FROM uuba_case_intake WHERE reference=:r"), {"r":reference}).first()\n    if not r:\n        raise _HTTP(404, "Case request not found")\n    return _row(r)\n\n@app.patch("/api/admin/case-intake/{reference}")\nasync def uuba_admin_case_intake_update(reference:str, request:_Req):\n    _admin(request)\n    _init()\n    try:\n        d = await request.json()\n    except Exception:\n        raise _HTTP(400, "Invalid request")\n    allowed={"status","scope_level","quote_amount","quote_notes","payment_reference","internal_notes","assigned_to"}\n    sets=[]\n    p={"r":reference}\n    for k in allowed:\n        if k not in d:\n            continue\n        v=d.get(k)\n        if k=="status" and v not in _STATUSES:\n            raise _HTTP(400, "Invalid status")\n        if k=="quote_amount":\n            if v in ("",None):\n                v=None\n            else:\n                try:\n                    v=round(float(v),2)\n                except Exception:\n                    raise _HTTP(400, "Quote must be a number")\n                if not 0 <= v <= 100000:\n                    raise _HTTP(400, "Quote is outside the permitted range")\n        elif k!="status":\n            v=_clean(v,10000)\n        p[k]=v\n        sets.append(f"{k}=:{k}")\n    if not sets:\n        raise _HTTP(400, "No changes supplied")\n    sets.append("updated_at=NOW()")\n    if d.get("status") in {"triage","scoped","quoted","accepted","payment_pending","in_review","qa","completed","declined"}:\n        sets.append("reviewed_at=COALESCE(reviewed_at,NOW())")\n    if d.get("status") in {"completed","declined"}:\n        sets.append("closed_at=NOW()")\n    elif "status" in d:\n        sets.append("closed_at=NULL")\n    with _eng.begin() as c:\n        r = c.execute(_sql("UPDATE uuba_case_intake SET "+",".join(sets)+" WHERE reference=:r RETURNING *"), p).first()\n    if not r:\n        raise _HTTP(404, "Case request not found")\n    return _row(r)\n'
FORM = '\n<section id="uuba-review-request" style="margin:34px auto;max-width:900px;background:#fff;border:1px solid #d7e0e8;border-radius:18px;padding:26px">\n<h2>Request a Personal Case Review</h2>\n<p>Initial scope assessment only. Uúba confirms availability, scope and price before substantive work begins.</p>\n<form id="uubaCaseReviewForm">\n<label>Full name<input name="name" required maxlength="200"></label>\n<label>Email<input name="email" type="email" required maxlength="320"></label>\n<label>Phone (optional)<input name="phone" maxlength="80"></label>\n<label>Dispute category<select name="category" required><option value="">Choose…</option><option>Car dealer / vehicle</option><option>New build / housing</option><option>Phone / broadband / pay TV</option><option>Retail / consumer goods</option><option>Trades / home services</option><option>Energy</option><option>Travel</option><option>Employment</option><option>Council / public services</option><option>Other consumer dispute</option></select></label>\n<label>Business / organisation involved<input name="trader_name" maxlength="240"></label>\n<label>Amount in dispute (optional)<input name="amount_in_dispute" maxlength="120"></label>\n<label>Important deadline (optional)<input name="deadline" maxlength="120"></label>\n<label>What has happened?<textarea name="summary" required minlength="40" maxlength="8000" rows="7"></textarea></label>\n<label>What outcome are you seeking?<textarea name="desired_outcome" maxlength="5000" rows="4"></textarea></label>\n<label>What evidence do you currently have?<textarea name="evidence_notes" maxlength="5000" rows="4"></textarea></label>\n<label><input type="checkbox" name="has_documents"> I have documents/evidence available if Uúba requests them.</label>\n<p><strong>Do not send sensitive documents at this stage.</strong></p>\n<label><input type="checkbox" name="privacy_consent" required> I understand this is an initial scope request only and does not mean Uúba has accepted my case or started substantive work.</label>\n<input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">\n<button type="submit">Send review request</button>\n<div id="uubaCaseReviewMessage" role="status"></div>\n</form></section>\n<style>\n#uuba-review-request label{display:block;margin:12px 0;font-weight:700}\n#uuba-review-request input,#uuba-review-request select,#uuba-review-request textarea{display:block;width:100%;box-sizing:border-box;padding:11px;margin-top:5px;border:1px solid #ccd6df;border-radius:8px}\n#uuba-review-request input[type=checkbox]{display:inline;width:auto}\n#uuba-review-request button{padding:12px 18px;background:#117f78;color:white;border:0;border-radius:8px;font-weight:800}\n</style>\n<script id="uuba-case-review-intake-js">\n(function(){\n const f=document.getElementById(\'uubaCaseReviewForm\'); if(!f)return;\n f.addEventListener(\'submit\',async e=>{\n  e.preventDefault();\n  const m=document.getElementById(\'uubaCaseReviewMessage\'),b=f.querySelector(\'button\');\n  b.disabled=true;m.textContent=\'Sending…\';\n  const fd=new FormData(f),d={};for(const [k,v] of fd.entries())d[k]=v;\n  d.has_documents=f.elements.has_documents.checked;d.privacy_consent=f.elements.privacy_consent.checked;\n  try{\n   const r=await fetch(\'/api/case-review/intake\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify(d)});\n   const x=await r.json().catch(()=>({})); if(!r.ok)throw new Error(x.detail||\'Request failed\');\n   m.innerHTML=\'<strong>Request received.</strong> Your Uúba reference is <strong>\'+x.reference+\'</strong>.\';f.reset();\n  }catch(x){m.textContent=x.message}finally{b.disabled=false}\n });\n})();\n</script>\n'
TERMS = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Personal Case Review Terms | Uúba</title></head><body style="font-family:Arial;line-height:1.6;max-width:900px;margin:40px auto;padding:0 20px"><h1>Personal Case Review terms</h1><p><strong>Scope first.</strong> A review request is not acceptance of a case and creates no obligation to pay. If Uúba can assist, scope, deliverables and price are confirmed before substantive work begins.</p><p><strong>Not a law firm.</strong> Uúba provides consumer-information, case-organisation and complaint-support services. It does not act as a solicitor, conduct litigation or provide regulated professional opinions.</p><p><strong>Deadlines.</strong> Submitting a request does not stop limitation periods, appeal dates or other deadlines.</p><p><strong>Paid work.</strong> No substantive paid review begins until scope and price are confirmed and any required cancellation/start-now information has been provided.</p><p><strong>Retention.</strong> Unaccepted or declined requests should normally be deleted or anonymised within 12 months after closure unless a lawful reason justifies longer retention. Accepted case and transaction records may be retained for up to 6 years where needed for legal, accounting, complaint or defence purposes.</p></body></html>'
ADMIN_WIDGET = '\n<section id="uuba-intake-queue" style="margin:28px 0;background:#fff;border:1px solid #d7e0e8;border-radius:16px;padding:22px">\n<h2>Personal Case Review intake</h2>\n<p><button onclick="uubaLoadIntake()">Refresh</button></p>\n<div id="uubaIntakeRows">Use Refresh to load intake requests.</div>\n</section>\n<script>\nasync function uubaLoadIntake(){\n const t=sessionStorage.getItem(\'helper_admin_token\')||\'\';\n const box=document.getElementById(\'uubaIntakeRows\');\n try{\n  const r=await fetch(\'/api/admin/case-intake\',{headers:{Authorization:\'Bearer \'+t}});\n  const d=await r.json(); if(!r.ok) throw new Error(d.detail||\'Request failed\');\n  box.innerHTML=d.items.length?d.items.map(x=>\'<div style="padding:10px 0;border-bottom:1px solid #eee"><strong>\'+x.reference+\'</strong> - \'+x.customer_name+\' - \'+x.category+\' - \'+x.status+\'</div>\').join(\'\'):\'No review requests yet.\';\n }catch(e){box.textContent=e.message}\n}\n</script>\n'

s = APP.read_text(encoding="utf-8")
if MARKER not in s:
    APP.write_text(s + "\n" + API + "\n", encoding="utf-8")

if CASE.exists():
    s = CASE.read_text(encoding="utf-8")
    if 'id="uuba-review-request"' not in s:
        s = s.replace("</body>", FORM + "\n<p style='text-align:center'><a href='/case-review-terms.html'>Personal Case Review terms</a></p></body>", 1)
        CASE.write_text(s, encoding="utf-8")

if CASEWORK.exists():
    s = CASEWORK.read_text(encoding="utf-8")
    if 'id="uuba-intake-queue"' not in s:
        s = s.replace("</body>", ADMIN_WIDGET + "\n</body>", 1)
        CASEWORK.write_text(s, encoding="utf-8")

(ROOT / "case-review-terms.html").write_text(TERMS, encoding="utf-8")

s = APP.read_text(encoding="utf-8")
route = '\n@app.get("/case-review-terms.html", response_class=HTMLResponse)\ndef uuba_case_review_terms():\n    return FileResponse(ROOT / "case-review-terms.html")\n'
if '@app.get("/case-review-terms.html"' not in s:
    APP.write_text(s + route, encoding="utf-8")

final = APP.read_text(encoding="utf-8")
assert MARKER in final
assert '@app.post("/api/case-review/intake")' in final
assert '@app.get("/api/admin/case-intake/summary")' in final
assert '@app.get("/case-review-terms.html"' in final
print("Uúba launch intake V4 installed successfully")


# ---- UUBA BILLING EXTENSION ----
from pathlib import Path
import re, shutil, subprocess, sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', 'stripe>=10,<20'])
ROOT=Path('/app')
app_path=ROOT/'app.py'
idx_path=ROOT/'index.html'
admin_path=ROOT/'admin.html'
req_path=ROOT/'requirements.txt'
app=app_path.read_text(encoding='utf-8')
idx=idx_path.read_text(encoding='utf-8')
# Repair an embedded closing </script> tag inside the printGeneratedLetter JavaScript.
# In HTML, a literal </script> terminates the surrounding script element even when it
# appears inside a JavaScript template/string, causing the remaining JS to render as text.
if 'function printGeneratedLetter' in idx:
    _ps = idx.index('function printGeneratedLetter')
    _pe = idx.find('async function deleteHelperDoc', _ps)
    if _pe == -1:
        _pe = min(len(idx), _ps + 12000)
    _pseg = idx[_ps:_pe]
    if '</script>' in _pseg:
        _pseg = _pseg.replace('</script>', '<\\/script>')
        idx = idx[:_ps] + _pseg + idx[_pe:]

admin=admin_path.read_text(encoding='utf-8')

# requirements
req=req_path.read_text(encoding='utf-8')
if 'stripe' not in req.lower():
    req += '\nstripe>=10,<20\n'
req_path.write_text(req,encoding='utf-8')

MARK='# UUBA BILLING V1'
if MARK not in app:
    billing = r'''

# UUBA BILLING V1
# Stripe-backed subscriptions and one-off purchases. Payment secrets are supplied only through environment variables.
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
STRIPE_PRICE_PLUS_MONTHLY = os.getenv("STRIPE_PRICE_PLUS_MONTHLY", "").strip()
STRIPE_PRICE_PLUS_YEARLY = os.getenv("STRIPE_PRICE_PLUS_YEARLY", "").strip()
STRIPE_PRICE_AI_REVIEW = os.getenv("STRIPE_PRICE_AI_REVIEW", "").strip()
UUBA_BILLING_ENFORCE = os.getenv("UUBA_BILLING_ENFORCE", "0").strip() == "1"

def _stripe():
    if not STRIPE_SECRET_KEY:
        raise HTTPException(503, "Payments are not yet connected.")
    try:
        import stripe
    except Exception:
        raise HTTPException(503, "Payment service is unavailable.")
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe

def init_billing_schema():
    con=db()
    if is_postgres(DATABASE_URL):
        con.execute("""CREATE TABLE IF NOT EXISTS uuba_billing(
          user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
          stripe_customer_id TEXT UNIQUE,
          stripe_subscription_id TEXT UNIQUE,
          plan TEXT NOT NULL DEFAULT 'core',
          billing_interval TEXT,
          status TEXT NOT NULL DEFAULT 'inactive',
          current_period_end TEXT,
          cancel_at_period_end INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS uuba_purchases(
          id BIGSERIAL PRIMARY KEY,
          user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          purchase_type TEXT NOT NULL,
          stripe_checkout_session_id TEXT UNIQUE,
          stripe_payment_intent_id TEXT,
          amount_pence INTEGER,
          status TEXT NOT NULL DEFAULT 'pending',
          credits INTEGER NOT NULL DEFAULT 0,
          consumed INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL)""")
    else:
        con.execute("""CREATE TABLE IF NOT EXISTS uuba_billing(
          user_id INTEGER PRIMARY KEY,
          stripe_customer_id TEXT UNIQUE,
          stripe_subscription_id TEXT UNIQUE,
          plan TEXT NOT NULL DEFAULT 'core',
          billing_interval TEXT,
          status TEXT NOT NULL DEFAULT 'inactive',
          current_period_end TEXT,
          cancel_at_period_end INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")
        con.execute("""CREATE TABLE IF NOT EXISTS uuba_purchases(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          purchase_type TEXT NOT NULL,
          stripe_checkout_session_id TEXT UNIQUE,
          stripe_payment_intent_id TEXT,
          amount_pence INTEGER,
          status TEXT NOT NULL DEFAULT 'pending',
          credits INTEGER NOT NULL DEFAULT 0,
          consumed INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_uuba_billing_customer ON uuba_billing(stripe_customer_id)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_uuba_purchase_user ON uuba_purchases(user_id,purchase_type,status)")
    con.commit(); con.close()

init_billing_schema()

def billing_row(user_id:int):
    con=db(); r=con.execute("SELECT * FROM uuba_billing WHERE user_id=?",(user_id,)).fetchone(); con.close(); return r

def user_has_plus(user_id:int)->bool:
    r=billing_row(user_id)
    return bool(r and r['plan']=='plus' and r['status'] in ('active','trialing','past_due'))

def _billing_dict(user_id:int):
    r=billing_row(user_id)
    if not r:
        return {"plan":"core","status":"active","billing_interval":None,"current_period_end":None,"cancel_at_period_end":False,"payments_connected":bool(STRIPE_SECRET_KEY)}
    return {"plan":r['plan'],"status":r['status'],"billing_interval":r['billing_interval'],"current_period_end":r['current_period_end'],"cancel_at_period_end":bool(r['cancel_at_period_end']),"payments_connected":bool(STRIPE_SECRET_KEY)}

def _ensure_customer(user):
    stripe=_stripe(); r=billing_row(user['id'])
    if r and r['stripe_customer_id']:
        return r['stripe_customer_id']
    customer=stripe.Customer.create(email=user['email'],name=user.get('name') or None,metadata={"uuba_user_id":str(user['id'])})
    ts=now_iso(); con=db()
    con.execute("""INSERT INTO uuba_billing(user_id,stripe_customer_id,plan,status,created_at,updated_at)
                   VALUES(?,?,'core','inactive',?,?)
                   ON CONFLICT(user_id) DO UPDATE SET stripe_customer_id=excluded.stripe_customer_id,updated_at=excluded.updated_at""",
                (user['id'],customer.id,ts,ts))
    con.commit(); con.close(); return customer.id

class PlusCheckoutIn(BaseModel):
    interval: str

@app.get('/api/billing/status')
def uuba_billing_status(request:Request):
    u=current_user(request)
    d=_billing_dict(u['id'])
    con=db();
    credit=con.execute("SELECT COALESCE(SUM(credits-consumed),0) n FROM uuba_purchases WHERE user_id=? AND purchase_type='ai_specialist_review' AND status='paid'",(u['id'],)).fetchone()[0]
    con.close(); d['ai_review_credits']=int(credit or 0); return d

@app.post('/api/billing/checkout/plus')
def uuba_plus_checkout(data:PlusCheckoutIn,request:Request):
    u=current_user(request,True); interval=data.interval.strip().lower()
    if interval not in ('monthly','annual'):
        raise HTTPException(400,'Choose monthly or annual billing.')
    price=STRIPE_PRICE_PLUS_MONTHLY if interval=='monthly' else STRIPE_PRICE_PLUS_YEARLY
    if not price:
        raise HTTPException(503,'This Plus billing option has not been connected yet.')
    stripe=_stripe(); customer=_ensure_customer(u)
    session=stripe.checkout.Session.create(
      customer=customer,mode='subscription',line_items=[{'price':price,'quantity':1}],
      success_url=BASE_URL+'/?payment=plus-success#billing-account',
      cancel_url=BASE_URL+'/?payment=cancelled#plans',
      allow_promotion_codes=True,
      subscription_data={'metadata':{'uuba_user_id':str(u['id']),'uuba_plan':'plus','uuba_interval':interval}},
      metadata={'uuba_user_id':str(u['id']),'uuba_type':'plus','uuba_interval':interval}
    )
    audit('plus_checkout_started',u['id'],{'interval':interval,'session':session.id})
    return {'url':session.url}

@app.post('/api/billing/checkout/ai-review')
def uuba_ai_review_checkout(request:Request):
    u=current_user(request,True)
    if not STRIPE_PRICE_AI_REVIEW:
        raise HTTPException(503,'The AI Specialist Review payment option has not been connected yet.')
    stripe=_stripe(); customer=_ensure_customer(u)
    session=stripe.checkout.Session.create(
      customer=customer,mode='payment',line_items=[{'price':STRIPE_PRICE_AI_REVIEW,'quantity':1}],
      success_url=BASE_URL+'/?payment=ai-review-success#specialist-help',
      cancel_url=BASE_URL+'/?payment=cancelled#plans',
      metadata={'uuba_user_id':str(u['id']),'uuba_type':'ai_specialist_review'}
    )
    ts=now_iso(); con=db(); con.execute("INSERT INTO uuba_purchases(user_id,purchase_type,stripe_checkout_session_id,status,credits,consumed,created_at,updated_at) VALUES(?, 'ai_specialist_review', ?, 'pending',0,0,?,?) ON CONFLICT(stripe_checkout_session_id) DO NOTHING",(u['id'],session.id,ts,ts)); con.commit(); con.close()
    audit('ai_review_checkout_started',u['id'],{'session':session.id})
    return {'url':session.url}

@app.post('/api/billing/portal')
def uuba_billing_portal(request:Request):
    u=current_user(request,True); r=billing_row(u['id'])
    if not r or not r['stripe_customer_id']:
        raise HTTPException(400,'No paid billing account exists yet.')
    stripe=_stripe(); s=stripe.billing_portal.Session.create(customer=r['stripe_customer_id'],return_url=BASE_URL+'/#billing-account')
    return {'url':s.url}

@app.post('/api/billing/cancel-plus')
def uuba_cancel_plus(request:Request):
    u=current_user(request,True); r=billing_row(u['id'])
    if not r or not r['stripe_subscription_id'] or r['plan']!='plus':
        raise HTTPException(400,'No active Plus subscription was found.')
    stripe=_stripe(); sub=stripe.Subscription.modify(r['stripe_subscription_id'],cancel_at_period_end=True)
    con=db(); con.execute("UPDATE uuba_billing SET cancel_at_period_end=1,updated_at=? WHERE user_id=?",(now_iso(),u['id'])); con.commit(); con.close()
    audit('plus_cancel_scheduled',u['id'],{'subscription':r['stripe_subscription_id']})
    return {'ok':True,'message':'Your Plus subscription will end at the end of the current paid period.','current_period_end':_billing_dict(u['id']).get('current_period_end')}

@app.post('/api/billing/resume-plus')
def uuba_resume_plus(request:Request):
    u=current_user(request,True); r=billing_row(u['id'])
    if not r or not r['stripe_subscription_id'] or r['plan']!='plus':
        raise HTTPException(400,'No Plus subscription was found.')
    stripe=_stripe(); stripe.Subscription.modify(r['stripe_subscription_id'],cancel_at_period_end=False)
    con=db(); con.execute("UPDATE uuba_billing SET cancel_at_period_end=0,updated_at=? WHERE user_id=?",(now_iso(),u['id'])); con.commit(); con.close()
    audit('plus_cancel_reversed',u['id'],{'subscription':r['stripe_subscription_id']})
    return {'ok':True}

def _subscription_interval(sub):
    try:
        return 'annual' if sub['items']['data'][0]['price']['recurring']['interval']=='year' else 'monthly'
    except Exception:
        return None

def _sync_subscription(sub):
    customer=sub.get('customer'); metadata=sub.get('metadata') or {}; uid=metadata.get('uuba_user_id')
    con=db()
    if not uid and customer:
        r=con.execute("SELECT user_id FROM uuba_billing WHERE stripe_customer_id=?",(customer,)).fetchone(); uid=str(r['user_id']) if r else None
    if not uid:
        con.close(); return
    status=sub.get('status') or 'inactive'; plan='plus' if status in ('active','trialing','past_due','unpaid','paused') else 'core'
    period=sub.get('current_period_end'); period_iso=datetime.fromtimestamp(period,timezone.utc).isoformat() if period else None
    ts=now_iso();
    con.execute("""INSERT INTO uuba_billing(user_id,stripe_customer_id,stripe_subscription_id,plan,billing_interval,status,current_period_end,cancel_at_period_end,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET stripe_customer_id=excluded.stripe_customer_id,stripe_subscription_id=excluded.stripe_subscription_id,plan=excluded.plan,billing_interval=excluded.billing_interval,status=excluded.status,current_period_end=excluded.current_period_end,cancel_at_period_end=excluded.cancel_at_period_end,updated_at=excluded.updated_at""",
      (int(uid),customer,sub.get('id'),plan,_subscription_interval(sub),status,period_iso,int(bool(sub.get('cancel_at_period_end'))),ts,ts))
    con.commit(); con.close()

@app.post('/api/stripe/webhook')
async def uuba_stripe_webhook(request:Request):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(503,'Webhook secret is not configured.')
    stripe=_stripe(); payload=await request.body(); sig=request.headers.get('stripe-signature','')
    try: event=stripe.Webhook.construct_event(payload,sig,STRIPE_WEBHOOK_SECRET)
    except Exception: raise HTTPException(400,'Invalid payment webhook.')
    typ=event['type']; obj=event['data']['object']
    if typ in ('customer.subscription.created','customer.subscription.updated','customer.subscription.deleted'):
        _sync_subscription(obj)
    elif typ=='checkout.session.completed':
        meta=obj.get('metadata') or {}; uid=meta.get('uuba_user_id'); kind=meta.get('uuba_type')
        if uid and kind=='ai_specialist_review' and obj.get('payment_status')=='paid':
            con=db(); con.execute("UPDATE uuba_purchases SET status='paid',credits=1,stripe_payment_intent_id=?,updated_at=? WHERE stripe_checkout_session_id=?",(obj.get('payment_intent'),now_iso(),obj.get('id'))); con.commit(); con.close(); audit('ai_review_paid',int(uid),{'session':obj.get('id')})
        elif kind=='case_review' and obj.get('payment_status')=='paid':
            ref=meta.get('case_reference')
            if ref:
                try:
                    # launch-intake table is created by the production launch patch
                    import sqlalchemy as _sa
                    _dbu=DATABASE_URL
                    if _dbu.startswith('postgres://'): _dbu='postgresql://'+_dbu[len('postgres://'):]
                    if _dbu:
                        _e=_sa.create_engine(_dbu,pool_pre_ping=True)
                        with _e.begin() as c: c.execute(_sa.text("UPDATE uuba_case_intake SET status='in_review',payment_reference=:p,updated_at=NOW() WHERE reference=:r"),{'p':obj.get('payment_intent') or obj.get('id'),'r':ref})
                except Exception: pass
    return {'received':True}

def consume_ai_review_credit(user_id:int)->bool:
    con=db(); r=con.execute("SELECT id,credits,consumed FROM uuba_purchases WHERE user_id=? AND purchase_type='ai_specialist_review' AND status='paid' AND consumed<credits ORDER BY id LIMIT 1",(user_id,)).fetchone()
    if not r: con.close(); return False
    con.execute("UPDATE uuba_purchases SET consumed=consumed+1,updated_at=? WHERE id=?",(now_iso(),r['id'])); con.commit(); con.close(); return True

@app.get('/api/admin/billing/summary')
def uuba_admin_billing_summary(request:Request):
    _require_caseworker_admin(request)
    con=db();
    plus=con.execute("SELECT COUNT(*) FROM uuba_billing WHERE plan='plus' AND status IN ('active','trialing','past_due')").fetchone()[0]
    monthly=con.execute("SELECT COUNT(*) FROM uuba_billing WHERE plan='plus' AND billing_interval='monthly' AND status IN ('active','trialing','past_due')").fetchone()[0]
    annual=con.execute("SELECT COUNT(*) FROM uuba_billing WHERE plan='plus' AND billing_interval='annual' AND status IN ('active','trialing','past_due')").fetchone()[0]
    reviews=con.execute("SELECT COUNT(*) FROM uuba_purchases WHERE purchase_type='ai_specialist_review' AND status='paid'").fetchone()[0]
    con.close(); return {'plus_total':int(plus),'plus_monthly':int(monthly),'plus_annual':int(annual),'ai_reviews_sold':int(reviews)}

@app.get('/api/admin/billing/subscriptions')
def uuba_admin_billing_subscriptions(request:Request):
    _require_caseworker_admin(request)
    con=db(); rows=con.execute("SELECT b.*,u.email FROM uuba_billing b JOIN users u ON u.id=b.user_id ORDER BY b.updated_at DESC LIMIT 250").fetchall(); con.close()
    return {'items':[dict(r) for r in rows]}

@app.post('/api/admin/case-intake/{reference}/payment-link')
def uuba_case_review_payment_link(reference:str,request:Request):
    _require_caseworker_admin(request); stripe=_stripe()
    # The launch-intake data lives in the same PostgreSQL DB but uses SQLAlchemy in the launch patch.
    try:
        import sqlalchemy as _sa
        _dbu=DATABASE_URL
        if _dbu.startswith('postgres://'): _dbu='postgresql://'+_dbu[len('postgres://'):]
        if not _dbu: raise Exception('database unavailable')
        _e=_sa.create_engine(_dbu,pool_pre_ping=True)
        with _e.begin() as c: row=c.execute(_sa.text("SELECT reference,email,customer_name,quote_amount,status FROM uuba_case_intake WHERE reference=:r"),{'r':reference}).mappings().first()
    except Exception: row=None
    if not row: raise HTTPException(404,'Case review request not found.')
    if row['quote_amount'] is None or float(row['quote_amount'])<=0: raise HTTPException(400,'Set the agreed quote before creating a payment link.')
    session=stripe.checkout.Session.create(
      mode='payment',customer_email=row['email'],
      line_items=[{'price_data':{'currency':'gbp','unit_amount':int(round(float(row['quote_amount'])*100)),'product_data':{'name':'Uúba Personal Case Review','description':f"Case review {reference}"}},'quantity':1}],
      success_url=BASE_URL+'/case-review.html?payment=success&reference='+reference,
      cancel_url=BASE_URL+'/case-review.html?payment=cancelled&reference='+reference,
      metadata={'uuba_type':'case_review','case_reference':reference}
    )
    try:
        with _e.begin() as c: c.execute(_sa.text("UPDATE uuba_case_intake SET status='payment_pending',payment_reference=:p,updated_at=NOW() WHERE reference=:r"),{'p':session.id,'r':reference})
    except Exception: pass
    return {'url':session.url,'reference':reference,'amount':float(row['quote_amount'])}
'''
    app += billing

# Gate live AI in Ask Uuba for Plus when enforcement enabled.
# Keep rules fallback available to Core.
app=app.replace("allow_live=bool(u.get('ai_enabled'))", "allow_live=bool(u.get('ai_enabled')) and (user_has_plus(u['id']) or not UUBA_BILLING_ENFORCE)")
app=app.replace("u.get('ai_enabled',False)", "u.get('ai_enabled',False) and (user_has_plus(u['id']) or not UUBA_BILLING_ENFORCE)")

# Core = one active case. Insert just before case creation INSERT.
needle="def create_case(data:CaseIn, request:Request):\n    u=current_user(request,True); check_rate(request,u['id'],30)"
if needle in app and 'Core includes one active case workspace' not in app:
    repl=needle+"\n    if UUBA_BILLING_ENFORCE and not user_has_plus(u['id']):\n        con=db(); n=con.execute(\"SELECT COUNT(*) FROM cases WHERE user_id=? AND status='Open'\",(u['id'],)).fetchone()[0]; con.close()\n        if n>=1: raise HTTPException(402,\"Core includes one active case workspace. Upgrade to Uúba Plus for multi-case support.\")"
    app=app.replace(needle,repl,1)

# Specialist review: consume one paid credit when enforcement is on.
needle2="def specialist_review(data:SpecialistReviewIn, request:Request):\n    u=current_user(request,True)"
if needle2 in app and 'AI Specialist Review requires a one-off purchase' not in app:
    repl2=needle2+"\n    if UUBA_BILLING_ENFORCE and not consume_ai_review_credit(u['id']):\n        raise HTTPException(402,\"AI Specialist Review requires a one-off purchase.\")"
    app=app.replace(needle2,repl2,1)

app_path.write_text(app,encoding='utf-8')

# Frontend paid flow
if 'id="uuba-billing-account"' not in idx:
    plus_old='<p class="muted">Provisional private-beta price.</p></article>'
    plus_new = "<div class=\"actions\" style=\"margin-top:16px\"><button class=\"btn\" type=\"button\" onclick=\"startPlusCheckout(\'monthly\')\">Choose monthly - &pound;14.99</button><button class=\"btn alt\" type=\"button\" onclick=\"startPlusCheckout(\'annual\')\">Choose annual - &pound;129</button></div><p class=\"muted\">Annual saves &pound;50.88 compared with 12 monthly payments. Renews automatically until cancelled. You can cancel online from your Uuba account.</p></article>"
    idx=idx.replace(plus_old,plus_new,1)
    ai_old='<p class="muted">Not legal advice or a prediction of outcome.</p></article>'
    ai_new="""<div class="actions" style="margin-top:16px"><button class="btn" type="button" onclick="startAiReviewCheckout()">Buy review - £34.99</button></div><p class="muted">One-off purchase. Not legal advice or a prediction of outcome.</p></article>"""
    idx=idx.replace(ai_old,ai_new,1)
    import base64 as _uuba_b64_main
    billing_html=_uuba_b64_main.b64decode("PHNlY3Rpb24gY2xhc3M9InNlY3Rpb24iIGlkPSJiaWxsaW5nLWFjY291bnQiPjxkaXYgY2xhc3M9InNlY3Rpb25oZWFkIj48ZGl2PjxzcGFuIGNsYXNzPSJ0YWciPkFjY291bnQgJiBiaWxsaW5nPC9zcGFuPjxoMj5Zb3VyIFXDumJhIHBsYW48L2gyPjxwPlNlZSB5b3VyIGN1cnJlbnQgcGxhbiwgcmVuZXdhbCBzdGF0dXMgYW5kIG1hbmFnZSBvciBjYW5jZWwgUGx1cyBvbmxpbmUuPC9wPjwvZGl2PjwvZGl2PjxhcnRpY2xlIGNsYXNzPSJjYXJkIiBpZD0idXViYS1iaWxsaW5nLWFjY291bnQiPjxoMyBpZD0idXViYVBsYW5OYW1lIj5Vw7piYSBDb3JlPC9oMz48cCBpZD0idXViYVBsYW5TdGF0dXMiIGNsYXNzPSJtdXRlZCI+U2lnbiBpbiB0byB2aWV3IHlvdXIgcGxhbi48L3A+PGRpdiBjbGFzcz0iYWN0aW9ucyIgaWQ9InV1YmFCaWxsaW5nQWN0aW9ucyI+PGJ1dHRvbiBjbGFzcz0iYnRuIiB0eXBlPSJidXR0b24iIG9uY2xpY2s9Im9wZW5BdXRoKCdsb2dpbicpIj5TaWduIGluPC9idXR0b24+PC9kaXY+PGRpdiBpZD0idXViYVBheW1lbnROb3RpY2UiIGNsYXNzPSJub3RpY2UiIHN0eWxlPSJkaXNwbGF5Om5vbmU7bWFyZ2luLXRvcDoxNHB4Ij48L2Rpdj48L2FydGljbGU+PC9zZWN0aW9uPg==").decode("utf-8")
    idx=idx.replace('<section class="section" id="about">',billing_html+'<section class="section" id="about">',1)

# Add Billing nav item after Plans
if '>Billing<' not in idx:
    idx=idx.replace('<a href="#plans">Plans</a>','<a href="#plans">Plans</a><a href="#billing-account">Billing</a>',1)

# JS flow appended before body close, avoids touching large existing script.
if 'UUBA_BILLING_UI_V1' not in idx:
    js=r'''
<script id="UUBA_BILLING_UI_V1">
let UUBA_PENDING_PURCHASE=null;
function uubaNeedAccount(kind){UUBA_PENDING_PURCHASE=kind;if(typeof openAuth==='function')openAuth('register');}
async function uubaPost(url,body){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':HELPER_CSRF||''},body:JSON.stringify(body||{})});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||'Request failed');return d}
window.startPlusCheckout=async function(interval){if(!HELPER_USER){uubaNeedAccount('plus:'+interval);return}try{const d=await uubaPost('/api/billing/checkout/plus',{interval});location.href=d.url}catch(e){alert(e.message)}}
window.startAiReviewCheckout=async function(){if(!HELPER_USER){uubaNeedAccount('ai-review');return}try{const d=await uubaPost('/api/billing/checkout/ai-review',{});location.href=d.url}catch(e){alert(e.message)}}
window.resumePendingPurchase=async function(){const p=UUBA_PENDING_PURCHASE;UUBA_PENDING_PURCHASE=null;if(!p)return;if(p.startsWith('plus:'))return startPlusCheckout(p.split(':')[1]);if(p==='ai-review')return startAiReviewCheckout()}
window.refreshBillingStatus=async function(){const name=document.getElementById('uubaPlanName'),status=document.getElementById('uubaPlanStatus'),actions=document.getElementById('uubaBillingActions');if(!name||!status||!actions)return;if(!HELPER_USER){name.textContent='Uúba Core';status.textContent='Sign in to view your plan.';actions.innerHTML='<button class="btn" type="button" onclick="openAuth(\'login\')">Sign in</button>';return}try{const r=await fetch('/api/billing/status');const d=await r.json();if(!r.ok)throw new Error(d.detail||'Unable to load billing');if(d.plan==='plus'){name.textContent='Uúba Plus';let bits=[d.billing_interval==='annual'?'Annual - £129/year':'Monthly - £14.99/month'];if(d.current_period_end)bits.push('Current period ends '+new Date(d.current_period_end).toLocaleDateString());if(d.cancel_at_period_end)bits.push('Cancellation scheduled');status.textContent=bits.join(' · ');actions.innerHTML='<button class="btn alt" type="button" onclick="openBillingPortal()">Manage billing</button>'+(d.cancel_at_period_end?'<button class="btn" type="button" onclick="resumePlus()">Keep Plus</button>':'<button class="btn" style="background:#991b1b" type="button" onclick="cancelPlus()">Cancel Plus</button>')}else{name.textContent='Uúba Core';status.textContent='Free plan · one active case workspace.';actions.innerHTML='<button class="btn" type="button" onclick="startPlusCheckout(\'monthly\')">Upgrade monthly - £14.99</button><button class="btn alt" type="button" onclick="startPlusCheckout(\'annual\')">Upgrade annual - £129</button>'}if(d.ai_review_credits>0)status.textContent+=' · '+d.ai_review_credits+' Specialist Review credit'+(d.ai_review_credits===1?'':'s')}catch(e){status.textContent=e.message}}
window.openBillingPortal=async function(){try{const d=await uubaPost('/api/billing/portal',{});location.href=d.url}catch(e){alert(e.message)}}
window.cancelPlus=async function(){if(!confirm('Cancel Uúba Plus at the end of the current paid period? You will keep Plus access until then.'))return;try{const d=await uubaPost('/api/billing/cancel-plus',{});alert(d.message);refreshBillingStatus()}catch(e){alert(e.message)}}
window.resumePlus=async function(){try{await uubaPost('/api/billing/resume-plus',{});refreshBillingStatus()}catch(e){alert(e.message)}}
(function(){const p=new URLSearchParams(location.search).get('payment');const box=document.getElementById('uubaPaymentNotice');if(p&&box){box.style.display='block';box.textContent=p.includes('success')?'Payment completed. Your account will update automatically once the payment confirmation arrives.':'Checkout cancelled - no new purchase was completed.'}setTimeout(()=>{if(typeof refreshBillingStatus==='function')refreshBillingStatus()},500)})();
</script>
'''
    # The production index has no real closing </body>; its only </body> occurs inside
    # the printGeneratedLetter popup template. Appending here keeps billing outside that
    # JavaScript string and prevents raw source from leaking into the rendered page.
    idx = idx + '\n' + js + '\n'

# Patch existing auth success/sign in/out to refresh billing and continue pending checkout.
idx=idx.replace("closeAuth();showSignedIn();await loadServerCases()", "closeAuth();showSignedIn();await loadServerCases();if(typeof refreshBillingStatus==='function')await refreshBillingStatus();if(typeof resumePendingPurchase==='function')await resumePendingPurchase()")
idx=idx.replace("document.getElementById('signOutBtn').style.display='inline-block'}", "document.getElementById('signOutBtn').style.display='inline-block';if(typeof refreshBillingStatus==='function')refreshBillingStatus()}",1)
idx=idx.replace("document.getElementById('signOutBtn').style.display='none'}", "document.getElementById('signOutBtn').style.display='none';if(typeof refreshBillingStatus==='function')refreshBillingStatus()}",1)

idx_path.write_text(idx,encoding='utf-8')

# Admin billing panel + quoted payment action documentation/visibility.
if 'id="uubaBillingAdmin"' not in admin:
    import base64 as _uuba_b64
    panel = _uuba_b64.b64decode("PHNlY3Rpb24gaWQ9InV1YmFCaWxsaW5nQWRtaW4iIHN0eWxlPSJtYXgtd2lkdGg6MTE4MHB4O21hcmdpbjoyMnB4IGF1dG87cGFkZGluZzowIDE4cHgiPgo8ZGl2IHN0eWxlPSJiYWNrZ3JvdW5kOiNmZmY7Ym9yZGVyOjFweCBzb2xpZCAjZDhlOGViO2JvcmRlci1yYWRpdXM6MTZweDtwYWRkaW5nOjIycHgiPgo8aDI+QmlsbGluZyAmIHN1YnNjcmlwdGlvbnM8L2gyPgo8cCBpZD0idXViYUJpbGxpbmdTdW1tYXJ5Ij5FbnRlciB0aGUgQWRtaW4gdG9rZW4gYWJvdmUsIHRoZW4gcmVmcmVzaCBiaWxsaW5nLjwvcD4KPGRpdiBzdHlsZT0iZGlzcGxheTpmbGV4O2dhcDoxMHB4O2ZsZXgtd3JhcDp3cmFwIj48YnV0dG9uIG9uY2xpY2s9ImxvYWRVdWJhQmlsbGluZ0FkbWluKCkiPlJlZnJlc2ggYmlsbGluZzwvYnV0dG9uPjwvZGl2Pgo8ZGl2IGlkPSJ1dWJhQmlsbGluZ0xpc3QiIHN0eWxlPSJtYXJnaW4tdG9wOjE2cHg7b3ZlcmZsb3c6YXV0byI+PC9kaXY+CjxwIHN0eWxlPSJmb250LXNpemU6MTNweDtjb2xvcjojNjA3Nzg2Ij5QZXJzb25hbCBDYXNlIFJldmlldyBwYXltZW50IGxpbmtzIGFyZSBjcmVhdGVkIG9ubHkgYWZ0ZXIgYSBxdW90ZSBoYXMgYmVlbiBzZXQuIEFQSTogPGNvZGU+UE9TVCAvYXBpL2FkbWluL2Nhc2UtaW50YWtlL3tyZWZlcmVuY2V9L3BheW1lbnQtbGluazwvY29kZT4uPC9wPgo8L2Rpdj48L3NlY3Rpb24+CjxzY3JpcHQgaWQ9InV1YmEtYWRtaW4tYmlsbGluZy1qcyI+CmFzeW5jIGZ1bmN0aW9uIGxvYWRVdWJhQmlsbGluZ0FkbWluKCl7CiBjb25zdCB0b2tlbj1zZXNzaW9uU3RvcmFnZS5nZXRJdGVtKCdoZWxwZXJfYWRtaW5fdG9rZW4nKXx8c2Vzc2lvblN0b3JhZ2UuZ2V0SXRlbSgndXViYV9hZG1pbl90b2tlbicpfHwnJzsKIGlmKCF0b2tlbil7ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3V1YmFCaWxsaW5nU3VtbWFyeScpLnRleHRDb250ZW50PSdFbnRlciB0aGUgQWRtaW4gdG9rZW4gZmlyc3QuJztyZXR1cm59CiBjb25zdCBoPXtBdXRob3JpemF0aW9uOidCZWFyZXIgJyt0b2tlbn07CiB0cnl7CiAgY29uc3QgcmVzcG9uc2VzPWF3YWl0IFByb21pc2UuYWxsKFsKICAgZmV0Y2goJy9hcGkvYWRtaW4vYmlsbGluZy9zdW1tYXJ5Jyx7aGVhZGVyczpofSksCiAgIGZldGNoKCcvYXBpL2FkbWluL2JpbGxpbmcvc3Vic2NyaXB0aW9ucycse2hlYWRlcnM6aH0pCiAgXSk7CiAgY29uc3QgYT1yZXNwb25zZXNbMF0sIGI9cmVzcG9uc2VzWzFdOwogIGNvbnN0IHM9YXdhaXQgYS5qc29uKCksIGQ9YXdhaXQgYi5qc29uKCk7CiAgaWYoIWEub2spIHRocm93IG5ldyBFcnJvcihzLmRldGFpbHx8J0JpbGxpbmcgc3VtbWFyeSBmYWlsZWQnKTsKICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgndXViYUJpbGxpbmdTdW1tYXJ5JykudGV4dENvbnRlbnQ9CiAgICdQbHVzOiAnK3MucGx1c190b3RhbCsnIHwgTW9udGhseTogJytzLnBsdXNfbW9udGhseSsnIHwgQW5udWFsOiAnK3MucGx1c19hbm51YWwrJyB8IEFJIHJldmlld3Mgc29sZDogJytzLmFpX3Jldmlld3Nfc29sZDsKICBpZigoZC5pdGVtc3x8W10pLmxlbmd0aCl7CiAgIGxldCByb3dzPScnOwogICBkLml0ZW1zLmZvckVhY2goZnVuY3Rpb24oeCl7CiAgICByb3dzICs9ICc8dHI+PHRkPicrKHguZW1haWx8fCcnKSsnPC90ZD48dGQ+JysoeC5wbGFufHwnJykrJzwvdGQ+PHRkPicrKHguYmlsbGluZ19pbnRlcnZhbHx8JycpKwogICAgICAgICAgICAnPC90ZD48dGQ+JysoeC5zdGF0dXN8fCcnKSsnPC90ZD48dGQ+JysoeC5jdXJyZW50X3BlcmlvZF9lbmR8fCcnKSsnPC90ZD48L3RyPic7CiAgIH0pOwogICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgndXViYUJpbGxpbmdMaXN0JykuaW5uZXJIVE1MPQogICAgJzx0YWJsZSBzdHlsZT0id2lkdGg6MTAwJTtib3JkZXItY29sbGFwc2U6Y29sbGFwc2UiPjx0cj48dGg+RW1haWw8L3RoPjx0aD5QbGFuPC90aD48dGg+SW50ZXJ2YWw8L3RoPjx0aD5TdGF0dXM8L3RoPjx0aD5QZXJpb2QgZW5kPC90aD48L3RyPicrcm93cysnPC90YWJsZT4nOwogIH1lbHNlewogICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgndXViYUJpbGxpbmdMaXN0JykudGV4dENvbnRlbnQ9J05vIGJpbGxpbmcgcmVjb3JkcyB5ZXQuJzsKICB9CiB9Y2F0Y2goZSl7ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3V1YmFCaWxsaW5nU3VtbWFyeScpLnRleHRDb250ZW50PWUubWVzc2FnZX0KfQo8L3NjcmlwdD4=").decode("utf-8")
    admin=admin.replace('</body>',panel+'\n</body>',1)
    admin_path.write_text(admin,encoding='utf-8')

# Environment examples
for fname in ['.env.example','.env.production.example']:
    p=ROOT/fname
    if p.exists():
        t=p.read_text(encoding='utf-8')
        if 'STRIPE_SECRET_KEY=' not in t:
            t += '''\n# Payments / billing\nSTRIPE_SECRET_KEY=\nSTRIPE_WEBHOOK_SECRET=\nSTRIPE_PRICE_PLUS_MONTHLY=\nSTRIPE_PRICE_PLUS_YEARLY=\nSTRIPE_PRICE_AI_REVIEW=\nUUBA_BILLING_ENFORCE=0\n'''
            p.write_text(t,encoding='utf-8')

# Create payment setup doc for production operator, not end users.
(ROOT/'PAYMENTS_SETUP.md').write_text('''# Uúba payments production setup\n\nThe application code now supports:\n- Uúba Plus monthly £14.99 subscription\n- Uúba Plus annual £129 subscription\n- £34.99 AI Specialist Review one-off purchase\n- Stripe customer portal\n- direct online cancellation at period end and resume\n- webhook-backed plan state\n- admin billing summary\n- quoted Personal Case Review checkout sessions\n\nRequired production environment variables:\n- STRIPE_SECRET_KEY\n- STRIPE_WEBHOOK_SECRET\n- STRIPE_PRICE_PLUS_MONTHLY\n- STRIPE_PRICE_PLUS_YEARLY\n- STRIPE_PRICE_AI_REVIEW\n- UUBA_BILLING_ENFORCE=1 after live products/prices and webhook have been verified\n\nWebhook endpoint: /api/stripe/webhook\nEvents: checkout.session.completed, customer.subscription.created, customer.subscription.updated, customer.subscription.deleted.\n\nDo not commit payment secret values to GitHub.\n''',encoding='utf-8')

print('billing patch applied')



# UUBA NEW BUILD DEFECT RESOLUTION CENTRE V1
_nb_backend='\n# UUBA NEW BUILD RESOLUTION CENTRE V1\nfrom pydantic import BaseModel as _NBBase, Field as _NBField\nfrom fastapi import Request as _NBRequest, HTTPException as _NBHTTP\n\ndef _nb_setup():\n    con=db()\n    try:\n        if is_postgres(DATABASE_URL):\n            con.execute("""CREATE TABLE IF NOT EXISTS uuba_newbuild_defects(\n              id BIGSERIAL PRIMARY KEY, user_id BIGINT NOT NULL, property_label_enc TEXT,\n              title_enc TEXT NOT NULL, location_enc TEXT, description_enc TEXT,\n              standard_ref_enc TEXT, developer_reply_enc TEXT, evidence_enc TEXT,\n              severity VARCHAR(16) NOT NULL DEFAULT \'medium\',\n              status VARCHAR(28) NOT NULL DEFAULT \'reported\',\n              reported_date VARCHAR(12), target_date VARCHAR(12),\n              created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")\n        else:\n            con.execute("""CREATE TABLE IF NOT EXISTS uuba_newbuild_defects(\n              id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, property_label_enc TEXT,\n              title_enc TEXT NOT NULL, location_enc TEXT, description_enc TEXT,\n              standard_ref_enc TEXT, developer_reply_enc TEXT, evidence_enc TEXT,\n              severity VARCHAR(16) NOT NULL DEFAULT \'medium\',\n              status VARCHAR(28) NOT NULL DEFAULT \'reported\',\n              reported_date VARCHAR(12), target_date VARCHAR(12),\n              created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")\n        con.execute(\'CREATE INDEX IF NOT EXISTS uuba_newbuild_owner ON uuba_newbuild_defects(user_id)\')\n        con.commit()\n    finally:\n        con.close()\n\n_NB_STATUSES={\'reported\',\'acknowledged\',\'disputed\',\'scheduled\',\'repair_claimed\',\'verified\',\'reopened\'}\n_NB_SEVERITIES={\'low\',\'medium\',\'high\',\'urgent\'}\nclass _NBDefect(_NBBase):\n    property_label: str=_NBField(default=\'\',max_length=140)\n    title: str=_NBField(min_length=3,max_length=220)\n    location: str=_NBField(default=\'\',max_length=160)\n    description: str=_NBField(default=\'\',max_length=5000)\n    standard_ref: str=_NBField(default=\'\',max_length=500)\n    developer_reply: str=_NBField(default=\'\',max_length=5000)\n    evidence: str=_NBField(default=\'\',max_length=3000)\n    severity: str=\'medium\'\n    status: str=\'reported\'\n    reported_date: str=_NBField(default=\'\',max_length=12)\n    target_date: str=_NBField(default=\'\',max_length=12)\n\ndef _nb_validate(data):\n    if data.severity not in _NB_SEVERITIES or data.status not in _NB_STATUSES:\n        raise _NBHTTP(400,\'Invalid defect category or status\')\n    for date in [data.reported_date, data.target_date]:\n        if date:\n            try:\n                from datetime import date as _date\n                if _date.fromisoformat(date).isoformat()!=date: raise ValueError()\n            except ValueError:\n                raise _NBHTTP(400,\'Dates must be YYYY-MM-DD\')\n\ndef _nb_row(r):\n    return {\'id\':r[\'id\'], \'property_label\':dec(r[\'property_label_enc\']),\n      \'title\':dec(r[\'title_enc\']), \'location\':dec(r[\'location_enc\']),\n      \'description\':dec(r[\'description_enc\']), \'standard_ref\':dec(r[\'standard_ref_enc\']),\n      \'developer_reply\':dec(r[\'developer_reply_enc\']), \'evidence\':dec(r[\'evidence_enc\']),\n      \'severity\':r[\'severity\'], \'status\':r[\'status\'],\n      \'reported_date\':r[\'reported_date\'] or \'\', \'target_date\':r[\'target_date\'] or \'\',\n      \'created_at\':r[\'created_at\'], \'updated_at\':r[\'updated_at\']}\n\n@app.get(\'/new-build-resolution\',response_class=HTMLResponse)\n@app.get(\'/new-build-resolution.html\',response_class=HTMLResponse)\ndef uuba_newbuild_page():\n    return FileResponse(ROOT/\'new-build-resolution.html\')\n\n@app.get(\'/api/newbuild/defects\')\ndef uuba_newbuild_list(request:_NBRequest):\n    u=current_user(request)\n    _nb_setup()\n    con=db()\n    try:\n        rows=con.execute(\'SELECT * FROM uuba_newbuild_defects WHERE user_id=? ORDER BY updated_at DESC,id DESC\',(u[\'id\'],)).fetchall()\n        return {\'items\':[_nb_row(x) for x in rows], \'count\':len(rows)}\n    finally: con.close()\n\n@app.post(\'/api/newbuild/defects\')\ndef uuba_newbuild_create(data:_NBDefect,request:_NBRequest):\n    u=current_user(request,True);check_rate(request,u[\'id\'],35)\n    _nb_validate(data);_nb_setup()\n    con=db()\n    try:\n        n=con.execute(\'SELECT COUNT(*) FROM uuba_newbuild_defects WHERE user_id=?\',(u[\'id\'],)).fetchone()[0]\n        if n>=250:raise _NBHTTP(400,\'Maximum of 250 defects per account; export the schedule before adding more.\')\n        ts=now_iso()\n        values=(u[\'id\'],enc(data.property_label),enc(data.title),enc(data.location),enc(data.description),enc(data.standard_ref),enc(data.developer_reply),enc(data.evidence),data.severity,data.status,data.reported_date,data.target_date,ts,ts)\n        if is_postgres(DATABASE_URL):\n            cur=con.execute("INSERT INTO uuba_newbuild_defects(user_id,property_label_enc,title_enc,location_enc,description_enc,standard_ref_enc,developer_reply_enc,evidence_enc,severity,status,reported_date,target_date,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) RETURNING id",values)\n            new_id=cur.fetchone()[0]\n        else:\n            cur=con.execute("INSERT INTO uuba_newbuild_defects(user_id,property_label_enc,title_enc,location_enc,description_enc,standard_ref_enc,developer_reply_enc,evidence_enc,severity,status,reported_date,target_date,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",values)\n            new_id=cur.lastrowid\n        con.commit()\n        r=con.execute(\'SELECT * FROM uuba_newbuild_defects WHERE id=? AND user_id=?\',(new_id,u[\'id\'])).fetchone()\n        return _nb_row(r)\n    finally:con.close()\n\n@app.put(\'/api/newbuild/defects/{defect_id}\')\ndef uuba_newbuild_update(defect_id:int,data:_NBDefect,request:_NBRequest):\n    u=current_user(request,True); check_rate(request,u[\'id\'],35)\n    _nb_validate(data);_nb_setup()\n    con=db()\n    try:\n        r=con.execute(\'SELECT id FROM uuba_newbuild_defects WHERE id=? AND user_id=?\',(defect_id,u[\'id\'])).fetchone()\n        if not r:raise _NBHTTP(404,\'Defect not found\')\n        values=(enc(data.property_label),enc(data.title),enc(data.location),enc(data.description),enc(data.standard_ref),enc(data.developer_reply),enc(data.evidence),data.severity,data.status,data.reported_date,data.target_date,now_iso(),defect_id,u[\'id\'])\n        con.execute("UPDATE uuba_newbuild_defects SET property_label_enc=?,title_enc=?,location_enc=?,description_enc=?,standard_ref_enc=?,developer_reply_enc=?,evidence_enc=?,severity=?,status=?,reported_date=?,target_date=?,updated_at=? WHERE id=? AND user_id=?",values)\n        con.commit()\n        return {\'ok\':True}\n    finally:con.close()\n\n@app.delete(\'/api/newbuild/defects/{defect_id}\')\ndef uuba_newbuild_delete(defect_id:int,request:_NBRequest):\n    u=current_user(request,True); check_rate(request,u[\'id\'],35)\n    _nb_setup()\n    con=db()\n    try:\n        r=con.execute(\'SELECT id FROM uuba_newbuild_defects WHERE id=? AND user_id=?\',(defect_id,u[\'id\'])).fetchone()\n        if not r:raise _NBHTTP(404,\'Defect not found\')\n        con.execute(\'DELETE FROM uuba_newbuild_defects WHERE id=? AND user_id=?\',(defect_id,u[\'id\']))\n        con.commit()\n        return {\'ok\':True}\n    finally:con.close()\n'
_nb_page='<!doctype html>\n<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>New Build Defect Resolution Centre | Uúba</title><meta name="description" content="Track outstanding new-build defects, organise developer replies and prepare structured follow-up correspondence."><style>\n:root{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:#123047;background:#f4f8fb}*{box-sizing:border-box}body{margin:0;line-height:1.55}a{color:#087d87}button,input,textarea,select{font:inherit}button{cursor:pointer}.bar{background:#fff;border-bottom:1px solid #dbe6ed}.bar-inner{max-width:1200px;margin:auto;padding:18px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px}.brand{font-weight:850;font-size:25px;color:#096b83;text-decoration:none;letter-spacing:-1px}.bar nav{display:flex;gap:18px;flex-wrap:wrap}.wrap{max-width:1200px;margin:auto;padding:28px 24px 65px}.hero{background:linear-gradient(120deg,#e8faf6,#e9f1ff);border:1px solid #c9e5e5;border-radius:22px;padding:32px;margin-bottom:24px}.eyebrow{text-transform:uppercase;letter-spacing:.09em;font-size:12px;color:#12757c;font-weight:800}.hero h1{font-size:clamp(28px,4vw,43px);letter-spacing:-1.3px;line-height:1.14;margin:12px 0}.hero p{max-width:830px}.chips{display:flex;gap:9px;flex-wrap:wrap}.chip{padding:7px 12px;background:#fff;border:1px solid #cfdee4;border-radius:40px;font-size:13px;font-weight:650}.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}.panel{background:#fff;border:1px solid #dce7ee;border-radius:18px;padding:23px;box-shadow:0 3px 17px #17375007;margin-bottom:20px}.panel h2{margin:0 0 9px;font-size:23px}.sub{color:#536b7b;font-size:14px}.full{grid-column:1/-1}.btn{border:0;border-radius:10px;background:#087c85;color:white;padding:11px 17px;font-weight:750}.btn.alt{background:#e8f5f6;color:#096770}.btn.outline{border:1px solid #a7c8cf;background:white;color:#096770}.btn.danger{background:#fff1f1;color:#a32e39}.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}.fields{display:grid;grid-template-columns:1fr 1fr;gap:13px}label{font-size:13px;font-weight:750;display:block}label input,label select,label textarea{margin-top:6px;width:100%;border:1px solid #bfcfd9;border-radius:9px;padding:10px;background:white;color:#123047}label textarea{min-height:94px;resize:vertical}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}.stat{background:white;border:1px solid #dce7ee;border-radius:14px;padding:14px}.stat strong{font-size:27px;display:block}.stat span{font-size:12px;color:#56707d}.items{display:grid;gap:12px}.item{border:1px solid #dce7ee;border-radius:13px;padding:15px;display:flex;justify-content:space-between;gap:18px}.item h3{margin:0 0 4px;font-size:17px}.pill{display:inline-block;background:#e9f5f8;border-radius:20px;padding:3px 9px;font-size:12px;font-weight:750;margin:4px 6px 4px 0}.urgent{background:#fff1e6;color:#974915}.muted{color:#607787}.note{border-left:4px solid #11a0a4;background:#eefafa;padding:12px 16px;border-radius:6px;font-size:14px}.notice{padding:12px;border-radius:9px;margin:10px 0;background:#fff6df;color:#664b12}.hide{display:none}.preview{white-space:pre-wrap;border:1px solid #dbe7ed;background:#f8fbfc;border-radius:10px;padding:16px;max-height:400px;overflow:auto}footer{margin-top:22px;font-size:13px;color:#647787}.links{display:flex;gap:15px;flex-wrap:wrap}.links a{font-weight:700}.empty{padding:25px;border:1px dashed #bdd0d6;border-radius:12px;color:#55717e;text-align:center}@media(max-width:780px){.grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.fields{grid-template-columns:1fr}.hero{padding:23px}.item{flex-direction:column}}@media print{.bar,.no-print,#form-panel,.btn{display:none!important}.wrap{max-width:none}body{background:#fff}.panel{break-inside:avoid}}\n</style></head><body><header class="bar"><div class="bar-inner"><a class="brand" href="/">Uúba ✦</a><nav><a href="/#cases">My cases</a><a href="/#plans">Plans</a><a href="/case-review.html">Personal Case Review</a></nav></div></header>\n<main class="wrap"><section class="hero"><div class="eyebrow">New-build homeowner tools</div><h1>New Build Defect Resolution Centre</h1><p>Move from a long list of snags to a clear record of what the developer has acknowledged, disputed, promised and actually repaired.</p><div class="chips"><span class="chip">Private defect tracker</span><span class="chip">Developer response organiser</span><span class="chip">Evidence checklist</span><span class="chip">Structured follow-up letters</span></div></section>\n<div id="account-banner" class="notice">Checking your Uúba account…</div><div class="stats"><div class="stat"><strong id="stat-all">0</strong><span>Recorded defects</span></div><div class="stat"><strong id="stat-open">0</strong><span>Not verified as repaired</span></div><div class="stat"><strong id="stat-disputed">0</strong><span>Disputed by developer</span></div><div class="stat"><strong id="stat-late">0</strong><span>Past target date</span></div></div>\n<div class="grid"><section class="panel" id="form-panel"><h2 id="form-title">Record a defect</h2><p class="sub">Only provide details you are comfortable storing in your Uúba account. Do not include other people\'s sensitive information.</p><form id="defect-form"><div class="fields"><label>Property nickname<input name="property_label" maxlength="140" placeholder="e.g. My new home"></label><label>Defect title (required)<input name="title" required minlength="3" maxlength="220" placeholder="e.g. Upstairs bedroom radiator undersized"></label><label>Location<input name="location" maxlength="160" placeholder="e.g. Bedroom 3"></label><label>Importance<select name="severity"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option><option value="urgent">Urgent — safety concern</option></select></label><label>Status<select name="status"><option value="reported">Reported</option><option value="acknowledged">Acknowledged</option><option value="disputed">Disputed</option><option value="scheduled">Work scheduled</option><option value="repair_claimed">Developer says repaired</option><option value="verified">Repair independently verified</option><option value="reopened">Reopened</option></select></label><label>Date first reported<input type="date" name="reported_date"></label><label>Developer target date<input type="date" name="target_date"></label><label>Relevant report / reference<input name="standard_ref" maxlength="500" placeholder="e.g. inspection item 47; technical verification required"></label><label class="full">Defect details<textarea name="description" maxlength="5000"></textarea></label><label class="full">Evidence already held (notes only)<textarea name="evidence" maxlength="3000" placeholder="Photographs dated…, thermal image…, report page…"></textarea></label><label class="full">Latest developer reply / promise<textarea name="developer_reply" maxlength="5000"></textarea></label></div><div class="actions"><button type="submit" class="btn" id="save-btn">Save defect</button><button type="button" class="btn outline hide" id="cancel-edit">Cancel edit</button></div><p class="sub" id="save-message" role="status"></p></form></section>\n<section class="panel"><h2>Follow-up and escalation</h2><p class="sub">Select the defects that remain unresolved, then prepare a structured follow-up to the developer.</p><div class="actions"><button class="btn alt" id="make-letter">Prepare developer letter</button><button class="btn outline" id="export-csv">Export defect schedule (CSV)</button></div><h3>What to check before escalating</h3><p class="note">Confirm the reservation date, developer\'s applicable consumer code, warranty provider and contractual documents. Different schemes can have different complaint routes and deadlines. This tool does not decide whether a Building Regulation has been breached.</p><div class="links"><a href="https://www.nhqb.org.uk/" target="_blank" rel="noopener noreferrer">New Homes Quality Board</a><a href="https://www.nhbc.co.uk/" target="_blank" rel="noopener noreferrer">NHBC</a><a href="https://www.citizensadvice.org.uk/consumer/" target="_blank" rel="noopener noreferrer">Citizens Advice</a></div><div class="actions"><a class="btn outline" style="text-decoration:none" href="/case-review.html">Request Personal Case Review</a></div><p class="sub">Limited availability. Scope and price confirmed before substantive work; complex reviews from £350 where appropriate. No percentage of compensation.</p><h3>Independent specialists</h3><p class="sub">For a technical finding, commission an appropriately qualified and insured surveyor, engineer, building-services specialist or other expert. Uúba does not inspect or certify physical properties.</p><a href="/specialists">Find independent guidance and specialists</a></section>\n<section class="panel full"><div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap"><div><h2>Your defect schedule</h2><p class="sub">Your records are private to your signed-in account. Change any defect when the developer replies or work is completed.</p></div><div class="actions"><label>Filter status<select id="status-filter"><option value="">All statuses</option><option value="open">Not verified</option><option value="disputed">Disputed</option><option value="verified">Verified</option></select></label></div></div><div class="items" id="defect-list"><div class="empty">Sign in to load your saved defects.</div></div></section>\n<section class="panel full hide" id="letter-panel"><h2>Draft developer follow-up</h2><p class="sub">Check every statement, date, reference and deadline before sending. This is a draft, not legal advice or a technical certification.</p><label>Developer / recipient<input id="letter-to" placeholder="Developer customer care"></label><label>Property reference (optional)<input id="letter-property" placeholder="e.g. plot number"></label><label>Letter<textarea readonly id="letter-output" style="min-height:300px"></textarea></label><div class="actions"><button class="btn" id="copy-letter">Copy text</button><button class="btn outline" onclick="window.print()">Print</button></div></section>\n<section class="panel full" id="report-check"><h2>Inspection report text checklist</h2><p class="sub">Paste a short extract from an inspection report. This checklist runs in your browser; pasted text is not sent to Uúba or stored. It flags missing context and cannot verify defects.</p><label>Report extract<textarea id="report-extract" maxlength="12000" style="min-height:160px" placeholder="Paste references, dates and relevant observations here…"></textarea></label><div class="actions"><button class="btn alt" type="button" id="analyse-extract">Check completeness</button></div><div class="note hide" id="extract-results" role="status" style="margin-top:14px"></div></section><section class="panel full"><h2>What this tool can — and cannot — analyse</h2><p>It can organise your inspection findings, identify missing dates, group unresolved issues, and build a clear developer correspondence schedule. It does not independently assess photographs, inspect a building, verify a regulation breach or produce an expert opinion.</p><p class="sub">An automated report-upload analyser would require a separate secure document-handling and technical verification workflow. That is not enabled in this initial release.</p></section></div><footer>Uúba provides consumer-information and case-organisation tools, not regulated legal advice or professional surveying. Sending a complaint does not suspend limitation periods or appeal deadlines. If a defect presents immediate danger, contact an appropriate emergency service or qualified professional.</footer></main>\n<script>\nlet csrf=\'\',items=[],editing=null;\nconst $=id=>document.getElementById(id);\nconst statusNames={reported:\'Reported\',acknowledged:\'Acknowledged\',disputed:\'Disputed\',scheduled:\'Work scheduled\',repair_claimed:\'Developer says repaired\',verified:\'Verified\',reopened:\'Reopened\'};\nconst esc=s=>String(s??\'\').replace(/[&<>"\']/g,ch=>({\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\',\'"\':\'&quot;\',"\'":\'&#39;\'}[ch]));\nasync function request(path,opts={}){const method=opts.method||\'GET\';const headers={\'Content-Type\':\'application/json\',...(opts.headers||{})};if(method!==\'GET\')headers[\'X-CSRF-Token\']=csrf;const r=await fetch(path,{credentials:\'same-origin\',...opts,headers});const x=await r.json().catch(()=>({}));if(!r.ok)throw Error(typeof x.detail===\'string\'?x.detail:\'Request failed\');return x;}\nasync function load(){try{const me=await request(\'/api/me\');csrf=me.csrf;$(\'account-banner\').textContent=\'Signed in as \'+me.user.email+\'. Your defect schedule is saved privately to your account.\';$(\'account-banner\').style.background=\'#e9faf4\';await refresh();}catch(e){$(\'account-banner\').innerHTML=\'Sign in to use the tracker. <a href="/#cases">Go to Uúba to sign in or create an account</a>.\';$(\'defect-list\').innerHTML=\'<div class="empty">Sign in on Uúba, then return here.</div>\';$(\'save-btn\').disabled=true;}}\nasync function refresh(){const data=await request(\'/api/newbuild/defects\');items=data.items||[];render();}\nfunction render(){const today=new Date().toISOString().slice(0,10);$(\'stat-all\').textContent=items.length;$(\'stat-open\').textContent=items.filter(x=>x.status!==\'verified\').length;$(\'stat-disputed\').textContent=items.filter(x=>x.status===\'disputed\').length;$(\'stat-late\').textContent=items.filter(x=>x.status!==\'verified\'&&x.target_date&&x.target_date<today).length;const filter=$(\'status-filter\').value;let chosen=items.filter(x=>!filter||(filter===\'open\'?x.status!==\'verified\':x.status===filter));$(\'defect-list\').innerHTML=chosen.length?chosen.map(x=>`<article class="item"><div><h3>${esc(x.title)}</h3><span class="pill">${esc(statusNames[x.status]||x.status)}</span><span class="pill ${x.severity===\'urgent\'?\'urgent\':\'\'}">${esc(x.severity)}</span><p class="sub">${esc(x.property_label||\'Property not specified\')} · ${esc(x.location||\'Location not specified\')} · Reported: ${esc(x.reported_date||\'Not dated\')}${x.target_date?\' · Target: \'+esc(x.target_date):\'\'}</p><div>${esc((x.description||\'\').slice(0,360))}</div>${x.developer_reply?\'<p class="sub"><b>Developer:</b> \'+esc(x.developer_reply.slice(0,240))+\'</p>\':\'\'}</div><div class="actions no-print"><button type="button" class="btn alt" data-edit="${x.id}">Edit</button><button type="button" class="btn danger" data-delete="${x.id}">Delete</button></div></article>`).join(\'\'):\'<div class="empty">No defects in this view. Add your first item above.</div>\';}\n$(\'defect-list\').addEventListener(\'click\',async e=>{const edit=e.target.closest(\'[data-edit]\'),del=e.target.closest(\'[data-delete]\');if(edit){const item=items.find(x=>x.id===Number(edit.dataset.edit));if(!item)return;editing=item.id;for(const [k,v] of Object.entries(item)){const input=$(\'defect-form\').elements.namedItem(k);if(input)input.value=v||\'\';}$(\'form-title\').textContent=\'Edit defect\';$(\'cancel-edit\').classList.remove(\'hide\');$(\'form-panel\').scrollIntoView({behavior:\'smooth\'});}if(del){if(!confirm(\'Delete this defect permanently?\'))return;try{await request(\'/api/newbuild/defects/\'+del.dataset.delete,{method:\'DELETE\'});await refresh();}catch(err){alert(err.message);}}});\n$(\'cancel-edit\').onclick=()=>{editing=null;$(\'defect-form\').reset();$(\'form-title\').textContent=\'Record a defect\';$(\'cancel-edit\').classList.add(\'hide\');};\n$(\'defect-form\').onsubmit=async e=>{e.preventDefault();const form=e.target,d=Object.fromEntries(new FormData(form).entries());$(\'save-btn\').disabled=true;$(\'save-message\').textContent=\'Saving…\';try{await request(editing?\'/api/newbuild/defects/\'+editing:\'/api/newbuild/defects\',{method:editing?\'PUT\':\'POST\',body:JSON.stringify(d)});$(\'save-message\').textContent=\'Saved to your account.\';$(\'cancel-edit\').click();await refresh();}catch(err){$(\'save-message\').textContent=err.message;}finally{$(\'save-btn\').disabled=false;}};\n$(\'status-filter\').onchange=render;\n$(\'export-csv\').onclick=()=>{if(!items.length){alert(\'Add some defects first.\');return;}const fields=[\'id\',\'property_label\',\'title\',\'location\',\'severity\',\'status\',\'reported_date\',\'target_date\',\'description\',\'evidence\',\'standard_ref\',\'developer_reply\'];const q=v=>\'"\'+String(v??\'\').replace(/"/g,\'""\')+\'"\';const csv=[fields.join(\',\'),...items.map(x=>fields.map(f=>q(x[f])).join(\',\'))].join(\'\\r\\n\');const blob=new Blob([\'\\ufeff\'+csv],{type:\'text/csv;charset=utf-8;\'});const link=document.createElement(\'a\');link.href=URL.createObjectURL(blob);link.download=\'uuba-defect-schedule.csv\';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);};\n$(\'make-letter\').onclick=()=>{const open=items.filter(x=>x.status!==\'verified\');if(!open.length){alert(\'There are no unresolved recorded defects.\');return;}const recipient=$(\'letter-to\').value||\'Developer customer care\';const prop=$(\'letter-property\').value||open.find(x=>x.property_label)?.property_label||\'the property\';const lines=open.map((x,i)=>`${i+1}. ${x.title} — ${x.location||\'location not recorded\'}; reported ${x.reported_date||\'date to confirm\'}; status: ${statusNames[x.status]||x.status}.${x.target_date?\' Target date: \'+x.target_date+\'.\':\'\'}${x.developer_reply?\' Latest response: \'+x.developer_reply.slice(0,450)+\'.\':\'\'}`).join(\'\\n\');$(\'letter-output\').value=`To: ${recipient}\\nSubject: Outstanding defects and request for written remedial programme — ${prop}\\n\\nDear Customer Care Team,\\n\\nI am writing to request a substantive update and clear remedial programme for the following defects that I have recorded as outstanding at ${prop}:\\n\\n${lines}\\n\\nPlease confirm for each item whether you accept it, any reason for disputing it, the proposed scope and method of repair, who will carry out the work, and the expected completion date. Please also identify any further inspection or technical evidence you require.\\n\\nI would appreciate a written response by [INSERT REASONABLE DATE]. Please confirm any applicable complaints procedure and warranty or consumer-code escalation route.\\n\\nI reserve my position regarding the unresolved issues and any applicable contractual, statutory and warranty rights.\\n\\nYours faithfully,\\n[YOUR NAME]`; $(\'letter-panel\').classList.remove(\'hide\');$(\'letter-panel\').scrollIntoView({behavior:\'smooth\'});};\n$(\'copy-letter\').onclick=async()=>{try{await navigator.clipboard.writeText($(\'letter-output\').value);alert(\'Copied\');}catch(e){$(\'letter-output\').select();document.execCommand(\'copy\');}};\n$(\'analyse-extract\').onclick=()=>{const raw=$(\'report-extract\').value.trim(),box=$(\'extract-results\');box.classList.remove(\'hide\');if(raw.length<50){box.textContent=\'Paste at least 50 characters to check the extract.\';return;}const checks=[[\'Inspection/report date\',/\\b(20\\d{2}[-\\/]\\d{1,2}[-\\/]\\d{1,2}|\\d{1,2}[-\\/]\\d{1,2}[-\\/]20\\d{2}|january|february|march|april|may|june|july|august|september|october|november|december)\\b/i],[\'Location of defect\',/\\b(bedroom|kitchen|bathroom|utility|loft|garage|hall|lounge|roof|garden|floor|window|door)\\b/i],[\'Item/report reference\',/\\b(item|ref|defect|section|photo|figure|image|number|no\\.)\\b/i],[\'Evidence or measurement\',/\\b(photo|photograph|picture|image|thermal|measurement|test|reading|mm|degrees)\\b/i],[\'Suggested next action\',/\\b(repair|replace|remedy|inspect|investigate|rectify|action|recommend)\\b/i]];const missing=checks.filter(([label,re])=>!re.test(raw)).map(([label])=>label);box.textContent=missing.length?\'Consider checking: \'+missing.join(\'; \')+\'. This is a completeness checklist, not an expert assessment.\':\'The text mentions dates, location, references, evidence and actions. Check accuracy against the original report. No technical conclusion has been made.\';};\nload();\n</script></body></html>'
_nb_app=APP.read_text(encoding='utf-8')
if '# UUBA NEW BUILD RESOLUTION CENTRE V1' not in _nb_app:
    APP.write_text(_nb_app+'\n'+_nb_backend+'\n',encoding='utf-8')
_nb_file=ROOT/'new-build-resolution.html'
_nb_file.write_text(_nb_page,encoding='utf-8')
_nb_idx=(ROOT/'index.html').read_text(encoding='utf-8')
if 'href="/new-build-resolution"' not in _nb_idx:
    _nb_link='<a href="/new-build-resolution" style="font-weight:800">New Build Resolution</a>'
    if '<a href="#cases">My cases</a>' in _nb_idx:
        _nb_idx=_nb_idx.replace('<a href="#cases">My cases</a>','<a href="#cases">My cases</a>'+_nb_link,1)
    else:
        _nb_idx=_nb_idx.replace('<nav class="nav">','<nav class="nav">'+_nb_link,1)
    # Add discovery card at a stable section boundary, never within the inline JavaScript.
    _nb_card='<section class="section" id="new-build-resolution"><div class="sectionhead"><div><span class="tag">New-build homeowner tools</span><h2>Defects recorded. Developer responses tracked.</h2><p>Keep a private defect schedule, monitor promised repairs and prepare structured follow-up correspondence.</p><p>Technical inspections and expert opinions come from appropriately qualified independent professionals.</p><a class="btn" href="/new-build-resolution">Open New Build Defect Resolution Centre</a></div></div></section>'
    if '<section class="section" id="plans">' in _nb_idx:
        _nb_idx=_nb_idx.replace('<section class="section" id="plans">',_nb_card+'<section class="section" id="plans">',1)
    (ROOT/'index.html').write_text(_nb_idx,encoding='utf-8')
print('New Build Defect Resolution Centre added')

