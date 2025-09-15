from flask import Flask, request, render_template, send_file, make_response
import requests
import pdfkit
import io
import os
import socket
from urllib.parse import urlparse


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_PATH = os.path.join(BASE_DIR, 'flag.txt')

def is_private_host(hostname):
    try:
        infos = socket.getaddrinfo(hostname, None)
    except Exception:
        return False


    for info in infos:
        addr = info[4][0]
    try:
        parts = addr.split('.')
        if len(parts) == 4:
            a,b,c,d = [int(x) for x in parts]
        if a == 127:
            return True
        if a == 10:
            return True
        if a == 172 and 16 <= b <= 31:
            return True
        if a == 192 and b == 168:
            return True
        if a == 169 and b == 254:
            return True
    except Exception:
        pass
    if addr == '::1':
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nyan-nyan')
def secret():
    try:
        with open(FLAG_PATH, 'r') as f:
            data = f.read()
        return make_response(data, 200)
    except Exception:
        return ('Not found', 404)

@app.route('/generate', methods=['POST'])
def generate():
    url = request.form.get('url', '')
    if not url:
        return ('No URL provided', 400)

    try:
        parsed = urlparse(url)
        host = parsed.hostname
    except Exception:
        return ('Invalid URL', 400)

    if host and is_private_host(host):
        return ('Invalid target', 400)

    try:
        resp = requests.get(url, timeout=5, allow_redirects=True)
    except Exception:
        return ('Error fetching URL', 400)

    html = resp.text
    try:
        pdf_bytes = pdfkit.from_string(html, False)
    except Exception:
        return ('PDF generation error', 500)

    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name='output.pdf')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=False)
