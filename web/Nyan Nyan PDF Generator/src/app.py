from flask import Flask, request, render_template, send_file, abort, make_response
import requests
import pdfkit
import io
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_PATH = os.path.join(BASE_DIR, 'flag.txt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/secret')
def secret():
    remote = request.remote_addr
    if remote not in ('127.0.0.1', '::1'):
        return ('Forbidden', 403)
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
        resp = requests.get(url, timeout=5, allow_redirects=True)
    except Exception as e:
        return (f'Error fetching URL: {e}', 400)

    html = resp.text
    try:
        pdf_bytes = pdfkit.from_string(html, False)
    except Exception as e:
        return (f'PDF generation error: {e}', 500)


    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name='output.pdf')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
