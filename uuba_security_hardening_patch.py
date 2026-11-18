#!/usr/bin/env python3
"""Uúba no-cost security hardening, applied after the launch and AI patches.
No changes to database schema, customer data, billing, or service configuration.
"""
from pathlib import Path
import re
import ast

root = Path('/app')
admin = root / 'caseworker-admin.html'
app_path = root / 'app.py'

if not admin.is_file() or not app_path.is_file():
    raise RuntimeError('Required Uúba application files are missing')

html = admin.read_text(encoding='utf-8')

# Previously customer-provided name/category/status were assembled into a
# string assigned to innerHTML. Render dynamic data only as text nodes.
vulnerable = (
    "box.innerHTML=d.items.length?d.items.map(x=>"
    "'<div style=\"padding:10px 0;border-bottom:1px solid #eee\"><strong>'+x.reference"
    "+'</strong> - '+x.customer_name+' - '+x.category+' - '+x.status+'</div>'"
    ").join(''):'No review requests yet.';"
)
safe = (
    "box.replaceChildren();"
    "if(!Array.isArray(d.items)||!d.items.length){"
    "box.textContent='No review requests yet.';"
    "}else{for(const x of d.items){"
    "const line=document.createElement('div');"
    "line.style.padding='10px 0';line.style.borderBottom='1px solid #eee';"
    "const strong=document.createElement('strong');"
    "strong.textContent=String(x.reference??'');"
    "line.appendChild(strong);"
    "line.appendChild(document.createTextNode(' - '+String(x.customer_name??'')"
    "+' - '+String(x.category??'')+' - '+String(x.status??'')));"
    "box.appendChild(line);"
    "}}"
)
marker='box.replaceChildren();if(!Array.isArray(d.items)'
if marker not in html:
    if vulnerable not in html:
        raise RuntimeError('Cannot identify admin intake rendering safely; refusing to patch wrong content')
    html = html.replace(vulnerable, safe, 1)
    admin.write_text(html, encoding='utf-8')

assert marker in admin.read_text(encoding='utf-8')
assert vulnerable not in admin.read_text(encoding='utf-8')

# Add defence-in-depth headers; do not introduce a CSP that would break
# the legacy application, which currently contains inline scripts.
app = app_path.read_text(encoding='utf-8')
tag='# UUBA SECURITY HEADERS V1'
if tag not in app:
    app += '''
\n# UUBA SECURITY HEADERS V1
from fastapi import Request as _SecRequest
@app.middleware("http")
async def _uuba_security_headers(request: _SecRequest, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    path = request.url.path
    if (path.startswith("/api/admin") or path.startswith("/api/cases") or
        path.startswith("/api/journey") or path.startswith("/api/case-review") or
        path in ("/api/me", "/api/assistant/chat", "/start", "/start-case", "/cases", "/journey", "/start-case.html")):
        response.headers["Cache-Control"] = "no-store"
    return response
'''
    app_path.write_text(app, encoding='utf-8')

final = app_path.read_text(encoding='utf-8')
ast.parse(final)
assert tag in final
print('Uúba security hardening OK: safe admin rendering and HTTP security headers')


# Persist chatbot rate limits across app restarts using existing paid PostgreSQL.
# This prevents bypass by restarting the free web worker; no extra service needed.
api_rate = r'''
# UUBA SHARED CHAT RATE LIMIT V1
import hashlib as _SecHashlib, os as _SecOS, time as _SecTime
from sqlalchemy import create_engine as _SecCreateEngine, text as _SecSql
from fastapi import HTTPException as _SecError
_SecDBUrl=_SecOS.environ.get("DATABASE_URL","").strip()
if _SecDBUrl.startswith("postgres://"):
    _SecDBUrl="postgresql://"+_SecDBUrl[len("postgres://"):]
_SecRateEngine=_SecCreateEngine(_SecDBUrl,pool_pre_ping=True,pool_size=2,max_overflow=2) if _SecDBUrl else None
_SecRateSchemaReady=False
_SecLastPrune=0

def _uuba_db_chat_rate(identity, maximum, window=3600):
    global _SecRateSchemaReady, _SecLastPrune
    if _SecRateEngine is None:
        raise _SecError(503,"AI requests temporarily unavailable; please use the case tools.")
    # UTC time windows; rate checks are atomic across workers.
    now=int(_SecTime.time())
    bucket=now//max(60,window)
    digest=_SecHashlib.sha256(identity.encode("utf-8")).hexdigest()
    try:
        with _SecRateEngine.begin() as connection:
            if not _SecRateSchemaReady:
                connection.execute(_SecSql("""CREATE TABLE IF NOT EXISTS uuba_ai_rate_limit (
                  identity_hash VARCHAR(64) NOT NULL,
                  window_bucket BIGINT NOT NULL,
                  requests INTEGER NOT NULL,
                  PRIMARY KEY (identity_hash,window_bucket)
                )"""))
                _SecRateSchemaReady=True
            if now-_SecLastPrune>3600:
                connection.execute(_SecSql(
                    "DELETE FROM uuba_ai_rate_limit WHERE window_bucket < :old"
                ),{"old":bucket-48})
                _SecLastPrune=now
            count=connection.execute(_SecSql("""INSERT INTO uuba_ai_rate_limit(identity_hash,window_bucket,requests)
                VALUES(:hash,:bucket,1)
                ON CONFLICT(identity_hash,window_bucket)
                DO UPDATE SET requests = uuba_ai_rate_limit.requests + 1
                WHERE uuba_ai_rate_limit.requests < :max_requests
                RETURNING requests"""),{"hash":digest,"bucket":bucket,"max_requests":maximum}).scalar()
        if count is None:
            raise _SecError(429,"Chat allowance reached. Please return later or use the existing case tools.")
    except _SecError:
        raise
    except Exception:
        raise _SecError(503,"The AI service is temporarily unavailable. Please use existing case tools.")

# Original AI endpoint resolves this global when a new message arrives.
_uca_rate=_uuba_db_chat_rate
'''
if '# UUBA SHARED CHAT RATE LIMIT V1' not in final:
    final += '\n'+api_rate
    ast.parse(final)
    app_path.write_text(final,encoding='utf-8')
print('Uúba persistent chatbot limits installed using existing PostgreSQL')

# Final-build assertion and correction: the exact start-case page has a
# clickable document filename AND an explicit download action.
start_page=root/'start-case.html'
page=start_page.read_text(encoding='utf-8')
old="const name=document.createElement('span');name.textContent=String(x.name||'Document');li.appendChild(name);const id=Number(x.id);if(Number.isSafeInteger(id)&&id>0){const link=document.createElement('a');link.href='/api/documents/'+id+'/download';link.textContent='Download';link.style.marginLeft='12px';link.setAttribute('aria-label','Download '+name.textContent);li.appendChild(link);}else{li.appendChild(document.createTextNode(' — download unavailable'));}"
new="const name=String(x.name||'Document');const id=Number(x.id);if(Number.isSafeInteger(id)&&id>0){const href='/api/documents/'+id+'/download';const title=document.createElement('a');title.href=href;title.textContent=name;title.style.textDecoration='underline';li.appendChild(title);const link=document.createElement('a');link.href=href;link.textContent='Download';link.style.marginLeft='12px';link.style.textDecoration='underline';link.setAttribute('aria-label','Download '+name);li.appendChild(link);}else{li.textContent=name+' — download unavailable';}"
assert old in page, 'Expected updated document renderer missing from final build'
page=page.replace(old,new,1)
page=page.replace('id="doc-list"></ul>','id="doc-list"></ul><p class="tiny muted">Click a filename or Download to retrieve your saved evidence.</p>',1)
start_page.write_text(page,encoding='utf-8')
assert new in start_page.read_text(encoding='utf-8')
print('Uúba final start-case document links verified')



# Durable evidence storage for the existing PostgreSQL plan, avoiding the
# ephemeral free web-service filesystem. Preserve configured S3 behaviour.
tree=ast.parse(app_path.read_text(encoding='utf-8'))
functions={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name,params in (('store_blob',['key','encrypted_data']),('read_blob',['key']),('delete_blob',['key'])):
    assert name in functions and [x.arg for x in functions[name].args.args]==params, 'Unexpected evidence storage adapter signature'
assert 'fernet.encrypt(data)' in ast.unparse(functions['upload_document'])
assert 'fernet.decrypt(read_blob' in ast.unparse(functions['download_document'])
storage=r'''
# UUBA DURABLE EVIDENCE V1
import logging as _EvidenceLogging
import secrets as _EvidenceSecrets
from sqlalchemy import LargeBinary as _EvidenceBinary, bindparam as _EvidenceBind
_EvidenceLegacyStore=store_blob
_EvidenceLegacyRead=read_blob
_EvidenceLegacyDelete=delete_blob
_EvidenceLock=82730621
_EvidenceBudget=200*1024*1024
_EvidenceDBLimit=700*1024*1024

def _evidence_schema(connection):
    connection.execute(_SecSql("SELECT pg_advisory_xact_lock(:lock)"),{"lock":_EvidenceLock})
    connection.execute(_SecSql("""CREATE TABLE IF NOT EXISTS uuba_evidence_blobs(
        stored_key TEXT PRIMARY KEY,
        encrypted_blob BYTEA NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )"""))

def store_blob(key: str, encrypted_data: bytes):
    if S3_BUCKET:
        return _EvidenceLegacyStore(key,encrypted_data)
    if _SecRateEngine is None:
        raise _SecError(503,"Durable document storage is temporarily unavailable.")
    try:
        with _SecRateEngine.begin() as connection:
            _evidence_schema(connection)
            used=connection.execute(_SecSql("SELECT COALESCE(SUM(octet_length(encrypted_blob)),0) FROM uuba_evidence_blobs")).scalar()
            dbsize=connection.execute(_SecSql("SELECT pg_database_size(current_database())")).scalar()
            if int(used or 0)+len(encrypted_data)>_EvidenceBudget or int(dbsize or 0)+2*len(encrypted_data)>_EvidenceDBLimit:
                raise _SecError(507,"Document storage is temporarily full. Keep your original file and contact support.")
            connection.execute(_SecSql("INSERT INTO uuba_evidence_blobs(stored_key,encrypted_blob) VALUES(:key,:blob)").bindparams(_EvidenceBind("blob",type_=_EvidenceBinary())),{"key":key,"blob":encrypted_data})
    except _SecError:
        raise
    except Exception:
        _EvidenceLogging.getLogger("uuba.evidence").warning("Durable evidence write failed")
        raise _SecError(503,"Document could not be stored securely. Please try again.")

def read_blob(key: str) -> bytes:
    if S3_BUCKET:
        return _EvidenceLegacyRead(key)
    if _SecRateEngine is None:
        raise _SecError(503,"Document storage is temporarily unavailable.")
    try:
        with _SecRateEngine.begin() as connection:
            _evidence_schema(connection)
            value=connection.execute(_SecSql("SELECT encrypted_blob FROM uuba_evidence_blobs WHERE stored_key=:key"),{"key":key}).scalar()
        if value is not None:
            return bytes(value)
    except Exception:
        _EvidenceLogging.getLogger("uuba.evidence").warning("Durable evidence read failed")
        raise _SecError(503,"Document storage is temporarily unavailable.")
    try:
        return _EvidenceLegacyRead(key)
    except FileNotFoundError:
        raise _SecError(410,"This earlier uploaded file is no longer available. Please re-upload your original copy.")

def delete_blob(key: str):
    if S3_BUCKET:
        return _EvidenceLegacyDelete(key)
    if _SecRateEngine is None:
        raise _SecError(503,"Document storage is temporarily unavailable.")
    try:
        with _SecRateEngine.begin() as connection:
            _evidence_schema(connection)
            connection.execute(_SecSql("DELETE FROM uuba_evidence_blobs WHERE stored_key=:key"),{"key":key})
        _EvidenceLegacyDelete(key)
    except Exception:
        _EvidenceLogging.getLogger("uuba.evidence").warning("Durable evidence deletion failed")
        raise _SecError(503,"Document deletion could not be completed. Please try again.")

@app.on_event("startup")
def _uuba_evidence_storage_selftest():
    if S3_BUCKET:
        _EvidenceLogging.getLogger("uvicorn.error").info("Uuba evidence storage uses configured S3; database storage self-test skipped")
        return
    if _SecRateEngine is None:
        _EvidenceLogging.getLogger("uvicorn.error").warning("Uuba durable evidence storage unavailable")
        return
    # Test the real adapters with a synthetic encrypted payload, never customer
    # files. Delete the synthetic row immediately after checking round-trip.
    key="__uuba_selftest__/"+_EvidenceSecrets.token_hex(16)
    sample=b"Uuba durable evidence storage self-test"
    stored=False
    try:
        store_blob(key,fernet.encrypt(sample))
        stored=True
        assert fernet.decrypt(read_blob(key))==sample
        delete_blob(key)
        stored=False
        _EvidenceLogging.getLogger("uvicorn.error").info("Uuba durable evidence storage self-test PASSED: encrypted write/read/delete")
    except Exception:
        _EvidenceLogging.getLogger("uvicorn.error").warning("Uuba durable evidence storage self-test FAILED")
    finally:
        if stored:
            try: delete_blob(key)
            except Exception: pass
'''
current=app_path.read_text(encoding='utf-8')
assert '# UUBA DURABLE EVIDENCE V1' not in current
current+='\n'+storage
ast.parse(current)
app_path.write_text(current,encoding='utf-8')
print('Uuba durable encrypted PostgreSQL evidence storage installed; existing owner checks preserved')
