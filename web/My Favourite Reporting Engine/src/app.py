from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import subprocess, uuid, os, shutil, pathlib

APP_DIR = pathlib.Path(__file__).parent.resolve()
BUILD_DIR = APP_DIR / "builds"
BUILD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = "ctf-dev-secret-change-me"

@app.route("/", methods=["GET","POST"])
def index():
    pdf_url = None
    log = ""
    if request.method == "POST":
        tex = request.form.get("latex", "")
        if not tex.strip():
            flash("Please provide some LaTeX content.", "warning")
            return redirect(url_for("index"))
        uid = uuid.uuid4().hex[:12]
        bd = BUILD_DIR / uid
        bd.mkdir()
        texfile = bd / "input.tex"
        content = tex
        texfile.write_text(content, encoding="utf-8")
        try:
            proc = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-shell-escape", "input.tex"],
                cwd=str(bd),
                capture_output=True,
                text=True,
                timeout=15
            )
            log = proc.stdout + "\n" + proc.stderr
        except subprocess.CalledProcessError as e:
            log = str(e)
        except Exception as e:
            log = "Execution error: " + str(e)
        pdf_path = bd / "input.pdf"
        if pdf_path.exists():
            pdf_url = f"/builds/{uid}/input.pdf"
        else:
            flash("PDF not produced. Check compilation log.", "danger")
    return render_template("index.html", log=log, pdf_url=pdf_url)

@app.route("/builds/<uid>/<filename>")
def serve_build(uid, filename):
    bd = BUILD_DIR / uid
    if not bd.exists():
        return "Not found", 404
    return send_from_directory(str(bd), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7001)
