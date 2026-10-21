FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ["Uuba-production-Render-PostgreSQL-uuba.co.uk-INLINE-LOGO-FIXED (1).zip", "/tmp/uuba.zip"]

RUN python -m zipfile -e /tmp/uuba.zip /app && rm /tmp/uuba.zip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data/uploads /app/data/backups && \
    useradd --create-home --uid 10001 uuba && \
    chown -R uuba:uuba /app

USER uuba
EXPOSE 10000

CMD ["sh","-c","python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips='*'"]
