#!/usr/bin/env python3
"""Minimal nc-only runner for GirlCTF Native Starlight."""

from __future__ import annotations

import os
import queue
import secrets
import shutil
import signal
import socketserver
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


TCP_HOST = "0.0.0.0"
TCP_PORT = int(os.environ.get("CHALLENGE_PORT", "1337"))
PAGE_PORT = int(os.environ.get("PAGE_PORT", "8000"))
MAX_PAYLOAD = 180_000
RUN_TIMEOUT = int(os.environ.get("RUN_TIMEOUT_SECONDS", "30"))
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "10"))
CHROME = os.environ.get("CHROME", "/opt/chrome-linux64/chrome")
FLAG_PATH = Path(os.environ.get("FLAG_PATH", "/flag/flag"))

SUBMISSIONS: dict[str, bytes] = {}
SUBMISSIONS_LOCK = threading.Lock()
ACTIVE_TOKEN: str | None = None
CHROME_LOCK = threading.Lock()


def load_flag() -> str:
    flag = FLAG_PATH.read_text(encoding="utf-8").strip()
    if not flag.startswith("gctf26{") or not flag.endswith("}"):
        raise RuntimeError("flag must use gctf26{...} format")
    if len(flag) > 96 or "\n" in flag or "\r" in flag:
        raise RuntimeError("flag must be a single line of at most 96 characters")
    return flag


def validate_config() -> None:
    if not 1 <= RUN_TIMEOUT <= 300:
        raise RuntimeError("RUN_TIMEOUT_SECONDS must be between 1 and 300")
    if not 1 <= MAX_ATTEMPTS <= 20:
        raise RuntimeError("MAX_ATTEMPTS must be between 1 and 20")
    if not Path(CHROME).is_file():
        raise RuntimeError(f"Chrome executable not found: {CHROME}")


FLAG = load_flag()


class PlayerPageHandler(BaseHTTPRequestHandler):
    """Serve only the submission currently assigned to Chrome."""

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        with SUBMISSIONS_LOCK:
            payload = SUBMISSIONS.get(ACTIVE_TOKEN or "")
        if parsed.path != "/exp.html" or payload is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_payload() -> tuple[bool, list[str], str]:
    profile = tempfile.mkdtemp(prefix="v8-2-profile-")
    Path("/tmp/v8ctf-home").mkdir(mode=0o700, exist_ok=True)
    target = f"http://127.0.0.1:{PAGE_PORT}/exp.html"
    command = [
        CHROME,
        "--headless=new",
        "--no-sandbox",
        "--disable-crashpad",
        "--disable-breakpad",
        "--disable-crash-reporter",
        "--disable-background-networking",
        "--disable-component-update",
        "--metrics-recording-only",
        "--noerrdialogs",
        "--enable-logging=stderr",
        f"--crash-dumps-dir={profile}",
        f"--user-data-dir={profile}",
        target,
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        start_new_session=True,
    )
    deadline = time.monotonic() + RUN_TIMEOUT
    traces: list[str] = []
    success = False
    reason = "renderer exited before the native ORW oracle"
    assert process.stderr is not None
    line_queue: queue.Queue[str | None] = queue.Queue()

    def drain_stderr() -> None:
        assert process.stderr is not None
        for stderr_line in process.stderr:
            line_queue.put(stderr_line)
        line_queue.put(None)

    threading.Thread(target=drain_stderr, daemon=True).start()
    try:
        while time.monotonic() < deadline:
            try:
                line = line_queue.get(timeout=0.25)
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if line is None:
                break
            marker_at = line.find("V8CTF-CAGE-RW:")
            if marker_at >= 0:
                marker = line[marker_at:].strip()
                traces.append(marker[:500])
                if "V8CTF-CAGE-RW:FAIL:" in marker:
                    reason = marker[:240]
                if "V8CTF-CAGE-RW:done" in marker:
                    if not reason.startswith("V8CTF-CAGE-RW:FAIL:"):
                        reason = "exploit stopped before native ORW"
                    break
            if FLAG in line:
                success = True
                reason = "native ORW printed the mounted flag"
                break
        else:
            reason = f"renderer time limit exceeded ({RUN_TIMEOUT}s)"
    finally:
        terminate_process_group(process)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        shutil.rmtree(profile, ignore_errors=True)
    return success, traces[-24:], reason


def execute_submission(
    payload: bytes,
    observer: Callable[[str, int, list[str], str], None] | None = None,
) -> tuple[bool, list[str], str]:
    global ACTIVE_TOKEN

    token = secrets.token_urlsafe(24)
    with SUBMISSIONS_LOCK:
        SUBMISSIONS[token] = payload
    all_traces: list[str] = []
    success = False
    reason = "no renderer reached the native ORW oracle"
    try:
        with CHROME_LOCK:
            with SUBMISSIONS_LOCK:
                ACTIVE_TOKEN = token
            try:
                for attempt in range(1, MAX_ATTEMPTS + 1):
                    if observer is not None:
                        observer("start", attempt, [], "opening a fresh renderer")
                    success, traces, reason = run_payload()
                    tagged = [f"try={attempt}:{trace}" for trace in traces]
                    all_traces.extend(tagged)
                    if observer is not None:
                        observer("finish", attempt, tagged, reason)
                    if success:
                        break
                    retryable = (
                        reason.startswith("renderer exited")
                        or reason.startswith("renderer time limit exceeded")
                        or reason.startswith("V8CTF-CAGE-RW:FAIL:")
                    )
                    if not retryable:
                        break
            finally:
                with SUBMISSIONS_LOCK:
                    ACTIVE_TOKEN = None
    finally:
        with SUBMISSIONS_LOCK:
            SUBMISSIONS.pop(token, None)
    return success, all_traces[-40:], reason


class ChallengeHandler(socketserver.StreamRequestHandler):
    def write(self, message: str) -> None:
        self.wfile.write(message.encode())
        self.wfile.flush()

    def handle(self) -> None:
        self.request.settimeout(20)
        self.write(
            "\n"
            " Hey hey girls or boi (xD, send me a good design of confession HTML to 150.0.7871.46 i will show u my /flag/flag.\n\n"
            f"  try not send me more than {MAX_PAYLOAD} bytes, and i only accept {MAX_ATTEMPTS} fresh renderers \n"
            " btw i'm a little shy so be nice! no sandboxing allowed\n"
            "Size> "
        )
        try:
            size = int(self.rfile.readline(32).strip(), 10)
        except (ValueError, OSError):
            self.write("Invalid size.\n")
            return
        if not 1 <= size <= MAX_PAYLOAD:
            self.write("Payload rejected: invalid size.\n")
            return
        self.write("HTML> ")
        payload = self.rfile.read(size)
        if len(payload) != size:
            self.write("Payload ended early.\n")
            return
        self.request.settimeout(None)

        def observe(
            event: str, attempt: int, traces: list[str], message: str
        ) -> None:
            if event == "start":
                self.write(f"[~] Fresh renderer {attempt}/{MAX_ATTEMPTS}\n")
            else:
                for trace in traces[-12:]:
                    self.write(f"    {trace}\n")
                if message:
                    self.write(f"    status: {message}\n")

        try:
            success, _, reason = execute_submission(payload, observe)
        except OSError:
            return
        if success:
            self.write(f"\n[+] Flag: {FLAG}\n")
        else:
            self.write(f"\n[-] Failed: {reason}.\n")


class ChallengeServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 32


def serve_player_page() -> None:
    ThreadingHTTPServer(("127.0.0.1", PAGE_PORT), PlayerPageHandler).serve_forever()


def main() -> None:
    validate_config()
    threading.Thread(target=serve_player_page, daemon=True).start()
    with ChallengeServer((TCP_HOST, TCP_PORT), ChallengeHandler) as server:
        print(f"v8-2 listening on {TCP_HOST}:{TCP_PORT}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
