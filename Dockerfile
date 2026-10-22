FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ["Uuba-production-Render-PostgreSQL-uuba.co.uk-INLINE-LOGO-FIXED (1).zip", "/tmp/uuba.zip"]

RUN python -m zipfile -e /tmp/uuba.zip /app && rm /tmp/uuba.zip

RUN python -c 'from pathlib import Path; p=Path("index.html"); s=p.read_text(encoding="utf-8"); s=s.replace("})();</script></body></html>`);w.document.close();w.print()","})();<\\/script></body></html>`);w.document.close();w.print()"); s=s.replace("\n<script id=\"helper-workspace-tabs\">\n","\n"); s=s.replace("Uúba"+chr(39)+"s verified guidance","Uúba"+chr(92)+chr(39)+"s verified guidance"); p.write_text(s,encoding="utf-8"); files=list(Path(".").rglob("*.html"))+list(Path(".").rglob("*.md")); repls={"£6.99":"£14.99","£59/year":"£129/year","£24.99":"£34.99"}; [(lambda q: q.write_text(__import__("functools").reduce(lambda t,kv:t.replace(kv[0],kv[1]),repls.items(),q.read_text(encoding="utf-8")),encoding="utf-8"))(q) for q in files]; remaining=[(str(q),old) for q in files for old in repls if old in q.read_text(encoding="utf-8")]; assert not remaining, "Old pricing remains: "+repr(remaining)'

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data/uploads /app/data/backups && \
    useradd --create-home --uid 10001 uuba && \
    chown -R uuba:uuba /app

USER uuba

EXPOSE 10000

CMD ["sh","-c","python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips='*'"]
