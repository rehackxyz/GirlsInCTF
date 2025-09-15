from flask import Flask, render_template, request
import psycopg2
import os
import re

app = Flask(__name__)

DB_HOST = os.environ.get("POSTGRES_HOST", "db")
DB_NAME = os.environ.get("POSTGRES_DB", "gctfdb")
DB_USER = os.environ.get("POSTGRES_USER", "gctfuser")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "gctfpass")
DB_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )



def waf_filter(payload: str) -> bool:
    if not payload:
        return False

    if re.search(r"\bunion\b", payload, re.IGNORECASE):
        return True

    if " " in payload:
        return True

    ua = request.headers.get("User-Agent", "").lower()
    if "sqlmap" in ua or "python-requests" in ua:
        return True
    return False


@app.route("/", methods=["GET"])
@app.route("/search", methods=["GET", "POST"])
def index():
    q = request.values.get("q", "")
    rows = []
    error = None

    if waf_filter(q):
        error = "Invalid search term."
        return render_template("index.html", q=q, rows=rows, error=error)

    sql = f"""
        SELECT id, name, price
        FROM products
        WHERE name ILIKE '%{q}%'
        ORDER BY id ASC
        LIMIT 25;
    """

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
    except Exception:

        error = "Invalid search term."

    return render_template("index.html", q=q, rows=rows, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False)
