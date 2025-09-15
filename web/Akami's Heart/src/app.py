from flask import Flask, request, abort, render_template_string, make_response
import os
import secrets
import json

app = Flask(__name__)

FLAG_PATH = "/flag.txt"
secret_blob = secrets.token_bytes(512)
if os.path.exists(FLAG_PATH):
    with open(FLAG_PATH, "rb") as f:
        secret_blob += f.read()
else:
    secret_blob += b"GCTF25{fake}\n"

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    """
    Vulnerable heartbeat-like endpoint.
    Expects JSON: {"payload": "...", "length": <int>}
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            raise ValueError("bad input")

        payload = data.get("payload", "")
        length = int(data.get("length", 0))

        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8", errors="ignore")
        else:
            payload_bytes = bytes(payload)

        extra_needed = length - len(payload_bytes)
        if extra_needed <= 0:
            resp = payload_bytes[:length]
        else:
            resp = payload_bytes + secret_blob[:extra_needed]

        r = make_response(resp)
        r.headers["Content-Type"] = "application/octet-stream"
        return r

    except Exception:
        return "💔 Ouch. My heart keeps bleeding", 400

@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Let me keep this memory deeply in my heart</title>
        <style>
            body {
                background: linear-gradient(135deg, #2b0033, #ff007f);
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                padding: 2em;
                border-radius: 20px;
                box-shadow: 0 0 20px rgba(255,0,127,0.7);
                text-align: center;
                width: 400px;
            }
            input, button {
                padding: 0.6em;
                margin: 0.5em;
                border-radius: 10px;
                border: none;
                outline: none;
            }
            input {
                width: 80%;
            }
            button {
                background: #ff007f;
                color: white;
                font-weight: bold;
                cursor: pointer;
            }
            pre {
                text-align: left;
                background: rgba(0,0,0,0.4);
                padding: 1em;
                border-radius: 10px;
                overflow-x: auto;
                max-height: 200px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>❤️ Akami's Heart ❤️</h2>
            <p>My heart is bleeding... can you cure and make her spill the secrets?</p>
            <input id="mystery" type="text" placeholder="Enter your data here...">
            <br>
            <button onclick="sendMystery()">Submit</button>
            <h3>Response:</h3>
            <pre id="resp">No response yet.</pre>
        </div>
        <script>
            async function sendMystery() {
                const input = document.getElementById("mystery").value;
                try {
                    const r = await fetch("/heartbeat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: input
                    });
                    const buf = await r.arrayBuffer();
                    const text = new TextDecoder().decode(buf);
                    document.getElementById("resp").textContent = text;
                } catch (e) {
                    document.getElementById("resp").textContent = "Error: " + e;
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
