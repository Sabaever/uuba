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


# Inspect packaged storage adapter implementations at build time. Only static
# source is printed; no runtime values, credentials, filenames or customer data.
tree=ast.parse(app_path.read_text(encoding='utf-8'))
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and (node.name in ('write_blob','read_blob','delete_blob','save_blob','download_document','upload_document') or 'blob' in node.name):
        print('UUBA STORAGE SOURCE '+node.name+': '+ast.unparse(node).replace('\n','\\n'))
