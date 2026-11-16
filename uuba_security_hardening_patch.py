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
        path in ("/api/me", "/api/assistant/chat")):
        response.headers["Cache-Control"] = "no-store"
    return response
'''
    app_path.write_text(app, encoding='utf-8')

final = app_path.read_text(encoding='utf-8')
ast.parse(final)
assert tag in final
print('Uúba security hardening OK: safe admin rendering and HTTP security headers')
