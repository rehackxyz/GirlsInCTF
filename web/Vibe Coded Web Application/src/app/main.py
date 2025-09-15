from flask import Flask, render_template, request
import psycopg2
import os

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


@app.route("/", methods=["GET"])
@app.route("/search", methods=["GET", "POST"])
def index():
    q = request.values.get("q", "")
    error = None
    rows = []

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
    except Exception as e:
        error = str(e)

    return render_template("index.html", q=q, rows=rows, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
