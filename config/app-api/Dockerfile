FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir \
    flask==3.0.3 \
    psycopg2-binary==2.9.9 \
    gunicorn==22.0.0

COPY app.py entrypoint.sh ./
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

USER nobody
EXPOSE 5000

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
