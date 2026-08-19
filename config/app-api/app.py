"""API ứng dụng — miền APP. Chỉ truy cập DB qua gateway-app-data."""

import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "gateway-app-data"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ.get("DB_NAME", "appdb"),
    "user": os.environ.get("DB_USER", "appuser"),
    "password": os.environ.get("DB_PASSWORD", "lab_password_change_me"),
    "connect_timeout": 5,
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "zone": "app"})


@app.route("/data")
def data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, value FROM records ORDER BY id")
        rows = [{"id": r[0], "name": r[1], "value": r[2]} for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({"records": rows})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


if __name__ == "__main__":
    bind = os.environ.get("BIND_ADDRESS", "127.0.0.1")
    port = int(os.environ.get("BIND_PORT", "5000"))
    app.run(host=bind, port=port)
