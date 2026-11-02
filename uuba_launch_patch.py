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
    with _eng.begin() as c: r = c.execute(q,p).first()
    return {"ok": True, "reference": r.reference, "message": "Received for initial scope assessment. Uúba has not yet accepted the case or started substantive work."}

@app.get("/api/admin/case-intake")
def uuba_admin_case_intake(request:_Req, status:str="", limit:int=100):
    _admin(request); _init(); limit=max(1,min(limit,250)); p={"limit":limit}; where=""
    if status:
        if status not in _STATUSES: raise _HTTP(400, "Invalid status")
        where=" WHERE status=:status"; p["status"]=status
    with _eng.begin() as c: rows = c.execute(_sql("SELECT * FROM uuba_case_intake"+where+" ORDER BY created_at DESC LIMIT :limit"), p).fetchall()
    return {"items": [_row(r) for r in rows], "count": len(rows)}

@app.get("/api/admin/case-intake/summary")
def uuba_admin_case_intake_summary(request:_Req):
    _admin(request); _init()
    with _eng.begin() as c: rows = c.execute(_sql("SELECT status,COUNT(*) n FROM uuba_case_intake GROUP BY status")).fetchall()
    n = {r.status:int(r.n) for r in rows}; out = {k:n.get(k,0) for k in _STATUSES}
    out["new_requests"] = n.get("new",0)
    out["active_reviews"] = sum(n.get(k,0) for k in ("accepted","payment_pending","in_review","qa"))
    return out

@app.get("/api/admin/case-intake/{reference}")
def uuba_admin_case_intake_detail(reference:str, request:_Req):
    _admin(request); _init()
    with _eng.begin() as c: r = c.execute(_sql("SELECT * FROM uuba_case_intake WHERE reference=:r"), {"r":reference}).first()
    if not r: raise _HTTP(404, "Case request not found")
    return _row(r)

@app.patch("/api/admin/case-intake/{reference}")
async def uuba_admin_case_intake_update(reference:str, request:_Req):
    _admin(request); _init()
    try: d = await request.json()
    except Exception: raise _HTTP(400, "Invalid request")
    allowed={"status","scope_level","quote_amount","quote_notes","payment_reference","internal_notes","assigned_to"}; sets=[]; p={"r":reference}
    for k in allowed:
        if k not in d: continue
        v=d.get(k)
        if k=="status" and v not in _STATUSES: raise _HTTP(400, "Invalid status")
        if k=="quote_amount":
            if v in ("",None): v=None
            else:
                try: v=round(float(v),2)
                except Exception: raise _HTTP(400, "Quote must be a number")
                if not 0 <= v <= 100000: raise _HTTP(400, "Quote is outside the permitted range")
        elif k!="status": v=_clean(v,10000)
        p[k]=v; sets.append(f"{k}=:{k}")
    if not sets: raise _HTTP(400, "No changes supplied")
    sets.append("updated_at=NOW()")
    if d.get("status") in {"triage","scoped","quoted","accepted","payment_pending","in_review","qa","completed","declined"}: sets.append("reviewed_at=COALESCE(reviewed_at,NOW())")
    if d.get("status") in {"completed","declined"}: sets.append("closed_at=NOW()")
    elif "status" in d: sets.append("closed_at=NULL")
    with _eng.begin() as c: r = c.execute(_sql("UPDATE uuba_case_intake SET "+",".join(sets)+" WHERE reference=:r RETURNING *"), p).first()
    if not r: raise _HTTP(404, "Case request not found")
    return _row(r)
'''

FORM = r'''
<section id="uuba-review-request" style="margin:34px auto;max-width:900px;background:#fff;border:1px solid #d7e0e8;border-radius:18px;padding:26px"><h2>Request a Personal Case Review</h2><p>Initial scope assessment only. Uúba confirms availability, scope and price before substantive work begins.</p><form id="uubaCaseReviewForm"><label>Full name<input name="name" required maxlength="200"></label><label>Email<input name="email" type="email" required maxlength="320"></label><label>Phone (optional)<input name="phone" maxlength="80"></label><label>Dispute category<select name="category" required><option value="">Choose…</option><option>Car dealer / vehicle</option><option>New build / housing</option><option>Phone / broadband / pay TV</option><option>Retail / consumer goods</option><option>Trades / home services</option><option>Energy</option><option>Travel</option><option>Employment</option><option>Council / public services</option><option>Other consumer dispute</option></select></label><label>Business / organisation involved<input name="trader_name" maxlength="240"></label><label>Amount in dispute (optional)<input name="amount_in_dispute" maxlength="120"></label><label>Important deadline (optional)<input name="deadline" maxlength="120"></label><label>What has happened?<textarea name="summary" required minlength="40" maxlength="8000" rows="7"></textarea></label><label>What outcome are you seeking?<textarea name="desired_outcome" maxlength="5000" rows="4"></textarea></label><label>What evidence do you currently have?<textarea name="evidence_notes" maxlength="5000" rows="4"></textarea></label><label><input type="checkbox" name="has_documents"> I have documents/evidence available if Uúba requests them.</label><p><strong>Do not send sensitive documents at this stage.</strong></p><label><input type="checkbox" name="privacy_consent" required> I understand this is an initial scope request only and does not mean Uúba has accepted my case or started substantive work.</label><input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true"><button type="submit">Send review request</button><div id="uubaCaseReviewMessage" role="status"></div></form></section><style>#uuba-review-request label{display:block;margin:12px 0;font-weight:700}#uuba-review-request input,#uuba-review-request select,#uuba-review-request textarea{display:block;width:100%;box-sizing:border-box;padding:11px;margin-top:5px;border:1px solid #ccd6df;border-radius:8px}#uuba-review-request input[type=checkbox]{display:inline;width:auto}#uuba-review-request button{padding:12px 18px;background:#117f78;color:white;border:0;border-radius:8px;font-weight:800}</style><script id="uuba-case-review-intake-js">(function(){const f=document.getElementById('uubaCaseReviewForm');if(!f)return;f.addEventListener('submit',async e=>{e.preventDefault();const m=document.getElementById('uubaCaseReviewMessage'),b=f.querySelector('button');b.disabled=true;m.textContent='Sending…';const fd=new FormData(f),d={};for(const [k,v] of fd.entries())d[k]=v;d.has_documents=f.elements.has_documents.checked;d.privacy_consent=f.elements.privacy_consent.checked;try{const r=await fetch('/api/case-review/intake',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}),x=await r.json().catch(()=>({}));if(!r.ok)throw new Error(x.detail||'Request failed');m.innerHTML='<strong>Request received.</strong> Your Uúba reference is <strong>'+x.reference+'</strong>.';f.reset()}catch(x){m.textContent=x.message}finally{b.disabled=false}})})();</script>
'''

TERMS='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Personal Case Review Terms | Uúba</title></head><body style="font-family:Arial;line-height:1.6;max-width:900px;margin:40px auto;padding:0 20px"><h1>Personal Case Review terms</h1><p><strong>Scope first.</strong> A review request is not acceptance of a case and creates no obligation to pay. If Uúba can assist, scope, deliverables and price are confirmed before substantive work begins.</p><p><strong>Not a law firm.</strong> Uúba provides consumer-information, case-organisation and complaint-support services. It does not act as a solicitor, conduct litigation or provide regulated professional opinions.</p><p><strong>Deadlines.</strong> Submitting a request does not stop limitation periods, appeal dates or other deadlines.</p><p><strong>Paid work.</strong> No substantive paid review begins until scope and price are confirmed and any required cancellation/start-now information has been provided.</p><p><strong>Retention.</strong> Unaccepted or declined requests should normally be deleted or anonymised within 12 months after closure unless a lawful reason justifies longer retention. Accepted case and transaction records may be retained for up to 6 years where needed for legal, accounting, complaint or defence purposes.</p></body></html>'''

s=APP.read_text(encoding='utf-8')
if MARKER not in s: APP.write_text(s+'\n'+API+'\n',encoding='utf-8')
if CASE.exists():
    s=CASE.read_text(encoding='utf-8')
    if 'id="uuba-review-request"' not in s:
        s=s.replace('</body>',FORM+"\n<p style='text-align:center'><a href='/case-review-terms.html'>Personal Case Review terms</a></p></body>",1)
        CASE.write_text(s,encoding='utf-8')
if CASEWORK.exists():
    s=CASEWORK.read_text(encoding='utf-8')
    if 'id="uuba-intake-queue"' not in s:
        widget=r'''<section id="uuba-intake-queue" style="margin:28px"><h2>Personal Case Review intake</h2><button onclick="uubaLoadIntake()">Refresh</button><pre id="uubaIntakeRows">Refresh to load requests.</pre></section><script id="uuba-case-intake-admin-js">async function uubaLoadIntake(){const t=sessionStorage.getItem('helper_admin_token')||'',r=await fetch('/api/admin/case-intake',{headers:{Authorization:'Bearer '+t}}),d=await r.json();document.getElementById('uubaIntakeRows').textContent=r.ok?d.items.map(x=>`${x.reference} | ${x.status} | ${x.customer_name} | ${x.email} | ${x.category} | ${x.quote_amount==null?'—':'£'+x.quote_amount}`).join('\n'):(d.detail||'Request failed')}</script>'''
        CASEWORK.write_text(s.replace('</body>',widget+'\n</body>',1),encoding='utf-8')
(ROOT/'case-review-terms.html').write_text(TERMS,encoding='utf-8')
s=APP.read_text(encoding='utf-8')
if '@app.get("/case-review-terms.html"' not in s:
    s+='''\n@app.get("/case-review-terms.html", response_class=HTMLResponse)\ndef uuba_case_review_terms():\n    return FileResponse(ROOT / "case-review-terms.html")\n'''
    APP.write_text(s,encoding='utf-8')
assert MARKER in APP.read_text(encoding='utf-8')
assert '@app.post("/api/case-review/intake")' in APP.read_text(encoding='utf-8')
print('Uúba launch patch installed')
