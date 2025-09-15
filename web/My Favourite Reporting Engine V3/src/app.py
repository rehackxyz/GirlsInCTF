from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import subprocess, uuid, pathlib, secrets
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

APP_DIR = pathlib.Path(__file__).parent.resolve()
BUILD_DIR = APP_DIR / "builds"
BUILD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = "latex-lates-latex-more-latex"

BLACKLIST = ["write18", "input", "\input", "\include", "include", "verbatim", "flag", "flag.txt", "catcode", "newread", "openin", "closein", "usepackage", "fileline", "verbatiminput", "newwrite", "outfile", "closeout", "immediate", "|", "includegraphics", "openout", "newcommand" "expandafter", "csname", "endcsname"]

signer = TimestampSigner(app.secret_key)

def is_blacklisted(tex: str) -> bool:
    lowered = tex.lower()
    for word in BLACKLIST:
        if word in lowered:
            return True
    return False

def make_nonce():
    return signer.sign(secrets.token_urlsafe(16)).decode()

def verify_nonce(token, max_age=60):
    try:
        signer.unsign(token, max_age=max_age)
        return True
    except (BadSignature, SignatureExpired):
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    pdf_url = None
    log = ""
    nonce = make_nonce()

    if request.method == "POST":
        tex = request.form.get("latex", "")
        token = request.form.get("nonce", "")

        if not verify_nonce(token):
            flash("Invalid or expired nonce.", "danger")
            return redirect(url_for("index"))

        if not tex.strip():
            flash("Please provide some LaTeX content.", "warning")
            return redirect(url_for("index"))

        if is_blacklisted(tex):
            flash("Blacklisted keyword detected in your LaTeX!", "danger")
            return redirect(url_for("index"))
            
        uid = uuid.uuid4().hex[:12]
        bd = BUILD_DIR / uid
        bd.mkdir()
        texfile = bd / "input.tex"
        texfile.write_text(tex, encoding="utf-8")

        subprocess.call(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", "input.tex"],
            cwd=str(bd),
            timeout=15
        )
        
        pdf_path = bd / "input.pdf"
        if pdf_path.exists():
            pdf_url = f"/builds/{uid}/input.pdf"
            log = "Compile success :D\n"
        else:
            log = "Compile error :(\n"

    return render_template("index.html", log=log, pdf_url=pdf_url, nonce=nonce)


@app.route("/builds/<uid>/<filename>")
def serve_build(uid, filename):
    bd = BUILD_DIR / uid
    if not bd.exists():
        return "Not found", 404
    return send_from_directory(str(bd), filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7002)
