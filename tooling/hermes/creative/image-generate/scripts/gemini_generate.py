#!/usr/bin/env python3
"""
Image generation via Gemini web UI using agent-browser + Xvfb.
Usage: python3 gemini_generate.py --prompt "..." [--output path.png]

Requirements:
  - agent-browser installed (npm install -g agent-browser)
  - google-chrome installed
  - Xvfb installed (sudo apt install xvfb)
  - Profile must be logged in. First-time login:
      google-chrome --remote-debugging-port=9222 --no-first-run \
        --user-data-dir=~/.openclaw/agents/main/agent/browser-profiles/gemini \
        https://gemini.google.com/app
    Sign in, then close Chrome.
"""
import argparse
import subprocess
import sys
import os
import json
import time
import shutil
import re
import socket
import urllib.request
import base64
import signal

# ---------------------------------------------------------------------------
# Profile dir
# ---------------------------------------------------------------------------

_OPENCLAW_PROFILE = os.path.expanduser(
    "~/.openclaw/agents/main/agent/browser-profiles/gemini"
)
_HERMES_PROFILE = os.path.expanduser("~/.hermes/browser-profiles/gemini")


def _resolve_profile_dir():
    if os.path.isdir(_OPENCLAW_PROFILE):
        return _OPENCLAW_PROFILE
    return _HERMES_PROFILE


PROFILE_DIR = _resolve_profile_dir()
SESSION_NAME = "gemini-img"
_chrome_proc = None
_xvfb_proc = None
_cdp_port = None
_display = None

# ---------------------------------------------------------------------------
# Xvfb
# ---------------------------------------------------------------------------

def _find_free_display():
    for n in range(99, 120):
        lock = f"/tmp/.X{n}-lock"
        if not os.path.exists(lock):
            return n
    return 99


def start_xvfb():
    global _xvfb_proc, _display
    display_num = _find_free_display()
    _display = f":{display_num}"
    _xvfb_proc = subprocess.Popen(
        ["Xvfb", _display, "-screen", "0", "1280x900x24", "-ac"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    return _display


def stop_xvfb():
    global _xvfb_proc
    if _xvfb_proc:
        _xvfb_proc.terminate()
        try:
            _xvfb_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _xvfb_proc.kill()
        _xvfb_proc = None

# ---------------------------------------------------------------------------
# CDP port
# ---------------------------------------------------------------------------

def _port_is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _port_has_chrome(port):
    try:
        with urllib.request.urlopen(
            f"http://localhost:{port}/json/version", timeout=2
        ) as r:
            data = json.loads(r.read())
            return "Chrome" in data.get("Browser", "")
    except Exception:
        return False


def _find_cdp_port():
    preferred = 9222
    if _port_is_free(preferred):
        return preferred, False
    if _port_has_chrome(preferred):
        return preferred, True
    for port in range(9223, 9231):
        if _port_is_free(port):
            return port, False
    raise RuntimeError("No free CDP port found in range 9222-9230")

# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------

def start_chrome(port, display):
    global _chrome_proc

    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        p = os.path.join(PROFILE_DIR, lock)
        if os.path.exists(p):
            os.remove(p)

    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if not chrome:
        print("ERROR: google-chrome not found.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(PROFILE_DIR, exist_ok=True)
    env = {**os.environ, "DISPLAY": display}

    _chrome_proc = subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            f"--user-data-dir={PROFILE_DIR}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )

    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            urllib.request.urlopen(
                f"http://localhost:{port}/json/version", timeout=2
            )
            return
        except Exception:
            time.sleep(0.5)

    print("ERROR: Chrome did not start in time", file=sys.stderr)
    cleanup()
    sys.exit(1)


def stop_chrome():
    global _chrome_proc
    if _chrome_proc:
        _chrome_proc.terminate()
        try:
            _chrome_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _chrome_proc.kill()
        _chrome_proc = None


def cleanup():
    stop_chrome()
    stop_xvfb()

# ---------------------------------------------------------------------------
# agent-browser helpers
# ---------------------------------------------------------------------------

def run(cmd, timeout=30, ignore_errors=False):
    full_cmd = ["agent-browser", "--session", SESSION_NAME] + cmd
    result = subprocess.run(
        full_cmd, capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0 and not ignore_errors:
        msg = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(msg or f"agent-browser failed: {' '.join(cmd)}")
    return result.stdout.strip()


def get_refs():
    out = run(["snapshot", "-i", "--json"])
    try:
        return json.loads(out).get("data", {}).get("refs", {})
    except Exception:
        return {}


def find_ref(refs, *keywords):
    for k, v in refs.items():
        name = v.get("name", "").lower()
        if all(kw.lower() in name for kw in keywords):
            return k
    return None


def get_body_text():
    return run(["eval", "document.body ? document.body.innerText.slice(0,2000) : ''"])


def fail(message):
    body = get_body_text()
    url = run(["get", "url"])
    print(f"ERROR: {message}", file=sys.stderr)
    print(f"URL: {url}", file=sys.stderr)
    snippet = re.sub(r"\s+", " ", body)[:400]
    if snippet:
        print(f"Page: {snippet}", file=sys.stderr)
    cleanup()
    sys.exit(1)

# ---------------------------------------------------------------------------
# Image extraction via CDP screenshot (most reliable — avoids CORS/blob issues)
# ---------------------------------------------------------------------------

def _cdp_screenshot(port):
    """Use CDP Page.captureScreenshot to get a PNG of the visible page."""
    import http.client, urllib.parse

    # Get the first target (page)
    conn = http.client.HTTPConnection("localhost", port, timeout=10)
    conn.request("GET", "/json/list")
    resp = conn.getresponse()
    targets = json.loads(resp.read())
    page_targets = [t for t in targets if t.get("type") == "page"]
    if not page_targets:
        return None
    ws_url = page_targets[0].get("webSocketDebuggerUrl", "")

    # WebSocket call to capture screenshot
    import websocket  # pip install websocket-client
    ws = websocket.create_connection(ws_url, timeout=15)
    ws.send(json.dumps({"id": 1, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    result = json.loads(ws.recv())
    ws.close()
    data = result.get("result", {}).get("data")
    if data:
        return base64.b64decode(data)
    return None


def extract_image_via_js(output_path):
    """
    Extract the generated image from the page using fetch() on blob URLs.
    Falls back to canvas if fetch fails.
    Returns True if successful.
    """
    js = """
(async function() {
  // Find generated images — look for blob: URLs or large http images in response containers
  const candidates = [];

  // 1. blob: images anywhere on page
  document.querySelectorAll('img[src^="blob:"]').forEach(img => {
    if ((img.naturalWidth || img.width) > 50) candidates.push(img);
  });

  // 2. https images in response area that aren't user avatars (>200px)
  if (!candidates.length) {
    document.querySelectorAll('img[src^="https"]').forEach(img => {
      const w = img.naturalWidth || img.width;
      const h = img.naturalHeight || img.height;
      if (w > 200 && h > 200) candidates.push(img);
    });
  }

  if (!candidates.length) return JSON.stringify({error: 'no images found'});

  const results = [];
  for (const img of candidates) {
    try {
      const resp = await fetch(img.src);
      const blob = await resp.blob();
      const ab = await blob.arrayBuffer();
      const arr = new Uint8Array(ab);
      let b = '';
      for (let i = 0; i < arr.byteLength; i++) b += String.fromCharCode(arr[i]);
      results.push({b64: btoa(b), w: img.naturalWidth||img.width, h: img.naturalHeight||img.height, type: blob.type});
    } catch(_) {
      try {
        const c = document.createElement('canvas');
        c.width = img.naturalWidth || img.width;
        c.height = img.naturalHeight || img.height;
        c.getContext('2d').drawImage(img, 0, 0);
        const url = c.toDataURL('image/png');
        if (url.length > 200) {
          results.push({b64: url.split(',')[1], w: c.width, h: c.height, type: 'image/png'});
        }
      } catch(__) {}
    }
  }

  return results.length
    ? JSON.stringify({images: results})
    : JSON.stringify({error: 'extraction failed for all candidates'});
})()
"""
    result = subprocess.run(
        ["agent-browser", "--session", SESSION_NAME, "eval", js, "--json"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return False

    try:
        outer = json.loads(result.stdout)
        raw = outer.get("data", {}).get("result", "{}")
        d = json.loads(raw)
    except Exception:
        return False

    if "error" in d:
        print(f"  JS extraction: {d['error']}", file=sys.stderr)
        return False

    images = d.get("images", [])
    if not images:
        return False

    saved = []
    for i, img in enumerate(images):
        data = base64.b64decode(img["b64"])
        ext = "jpg" if "jpeg" in img.get("type", "") else "png"
        if i == 0:
            path = output_path
        else:
            base = output_path.rsplit(".", 1)[0]
            path = f"{base}_{i+1}.{ext}"
        with open(path, "wb") as f:
            f.write(data)
        size_kb = len(data) // 1024
        print(f"✓ Saved: {path}")
        print(f"Size: {size_kb} KB ({img['w']}x{img['h']})")
        saved.append(path)

    return bool(saved)

# ---------------------------------------------------------------------------
# Delete current conversation
# ---------------------------------------------------------------------------

def delete_current_conversation():
    print("Deleting conversation from sidebar...", file=sys.stderr)
    try:
        time.sleep(1)

        # First try: use the "開啟對話動作選單" button already in refs
        # (it appears next to the active/selected conversation item)
        refs = get_refs()
        menu_ref = (
            find_ref(refs, "開啟對話動作選單")
            or find_ref(refs, "更多選項")
            or find_ref(refs, "More options")
        )

        if not menu_ref:
            # Second try: trigger hover via JS to reveal the hidden menu button
            hover_js = """
(function(){
  // Try various selectors for the active conversation
  const selectors = [
    'a[aria-current="page"]',
    '[data-active="true"]',
    '[data-selected="true"]',
    '.conversation-item--active',
    '[aria-selected="true"]',
  ];
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      el.dispatchEvent(new MouseEvent('mouseover', {bubbles:true}));
      el.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
      el.dispatchEvent(new MouseEvent('mousemove', {bubbles:true}));
      return 'hovered:' + sel;
    }
  }
  // Fallback: hover all conversation links and look for menu buttons appearing
  const links = document.querySelectorAll('nav a, [role="listitem"] a');
  if (links.length) {
    links[0].dispatchEvent(new MouseEvent('mouseover', {bubbles:true}));
    return 'hovered first link';
  }
  return 'nothing to hover';
})()
"""
            hover_result = run(["eval", hover_js], ignore_errors=True)
            print(f"  Hover result: {hover_result}", file=sys.stderr)
            time.sleep(1)

            refs = get_refs()
            menu_ref = (
                find_ref(refs, "開啟對話動作選單")
                or find_ref(refs, "更多選項")
                or find_ref(refs, "More options")
            )

        if not menu_ref:
            print("WARNING: Cannot find conversation menu — skipping delete", file=sys.stderr)
            return

        run(["click", f"@{menu_ref}"])
        time.sleep(0.8)

        refs = get_refs()
        delete_ref = find_ref(refs, "刪除") or find_ref(refs, "Delete")
        if not delete_ref:
            print("WARNING: Cannot find Delete option — skipping delete", file=sys.stderr)
            return

        run(["click", f"@{delete_ref}"])
        time.sleep(0.8)

        # Confirm dialog if present
        refs = get_refs()
        confirm_ref = (
            find_ref(refs, "確認")
            or find_ref(refs, "Confirm")
            or find_ref(refs, "確定")
        )
        if confirm_ref:
            run(["click", f"@{confirm_ref}"])
            time.sleep(0.5)

        print("✓ Conversation deleted", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: Delete conversation failed: {e}", file=sys.stderr)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(prompt, output):
    global _cdp_port

    if not shutil.which("agent-browser"):
        print("ERROR: agent-browser not found. Run: npm install -g agent-browser", file=sys.stderr)
        sys.exit(1)
    if not shutil.which("Xvfb"):
        print("ERROR: Xvfb not found. Run: sudo apt install xvfb", file=sys.stderr)
        sys.exit(1)

    port, chrome_running = _find_cdp_port()
    _cdp_port = port

    if chrome_running:
        print(f"Reusing Chrome on port {port}...", file=sys.stderr)
        display = os.environ.get("DISPLAY", ":0")
    else:
        print("Starting Xvfb virtual display...", file=sys.stderr)
        display = start_xvfb()
        print(f"Starting Chrome on port {port} (DISPLAY={display})...", file=sys.stderr)
        start_chrome(port, display)

    # Connect session
    subprocess.run(
        ["agent-browser", "--session", SESSION_NAME, "connect", str(port)],
        capture_output=True,
    )

    # Load Gemini with retry on network errors
    print("Opening Gemini...", file=sys.stderr)
    loaded = False
    for attempt in range(3):
        run(["open", "https://gemini.google.com/app"])
        run(["wait", "--load", "domcontentloaded"], ignore_errors=True)
        time.sleep(4)

        body = get_body_text()
        url = run(["get", "url"])

        if "網際網路" in body or "internet" in body.lower() or "connection" in body.lower():
            print(f"  Network error on attempt {attempt+1}, retrying...", file=sys.stderr)
            time.sleep(3)
            continue

        if "signin" in url.lower() or "登入" in body or "sign in" in body.lower():
            print(
                f"ERROR: Not logged in. Re-login:\n"
                f"  DISPLAY={display} google-chrome --remote-debugging-port={port} "
                f"--user-data-dir={PROFILE_DIR} https://gemini.google.com/app",
                file=sys.stderr,
            )
            cleanup()
            sys.exit(1)

        loaded = True
        break

    if not loaded:
        fail("Cannot load Gemini after 3 attempts — check network connection")

    refs = get_refs()

    # Activate image generation mode
    print("Activating image generation mode...", file=sys.stderr)
    img_btn = None
    for kw_set in [("生成圖片",), ("生成", "圖片"), ("Generate image",), ("Image",)]:
        img_btn = find_ref(refs, *kw_set)
        if img_btn:
            break
    if not img_btn:
        fail("Cannot find image generation button")

    run(["click", f"@{img_btn}"])
    time.sleep(1.5)

    # Find input and submit
    print(f"Submitting prompt...", file=sys.stderr)
    refs = get_refs()
    textbox = None
    for role_check in refs.values():
        if role_check.get("role") == "textbox":
            # get its key
            break
    for k, v in refs.items():
        if v.get("role") == "textbox":
            textbox = k
            break
    if not textbox:
        fail("Cannot find text input")

    run(["fill", f"@{textbox}", prompt])
    run(["press", "Enter"])

    # Wait for generation — detect by: 停止回覆 disappears OR 下載 appears
    print("Waiting for image generation...", file=sys.stderr)
    deadline = time.time() + 180
    done = False
    while time.time() < deadline:
        time.sleep(4)
        refs = get_refs()
        names = {v.get("name", "") for v in refs.values()}

        has_stop = any("停止回覆" in n or "Stop" in n for n in names)
        has_download = any("下載" in n or "download" in n.lower() for n in names)
        has_error = any("無法" in n or "錯誤" in n for n in names)
        generating = any("Creating" in n or "Generating" in n for n in names)

        elapsed = int(time.time() - (deadline - 180))
        print(f"  [{elapsed}s] stop={has_stop} download={has_download} generating={generating}", file=sys.stderr)

        if has_error:
            fail("Gemini reported an error")

        if has_download:
            print("  → Download button detected!", file=sys.stderr)
            done = True
            break

        if not has_stop and not generating and elapsed > 8:
            print("  → Generation appears complete (stop button gone)", file=sys.stderr)
            done = True
            break

    if not done:
        fail("Image generation timed out after 180s")

    # Build output path
    ts = int(time.time())
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt[:30]).strip("-")
    if not output:
        output = f"/tmp/gemini-img-{slug}-{ts}.png"

    print("Extracting image...", file=sys.stderr)
    time.sleep(1)
    ok = extract_image_via_js(output)

    if not ok:
        fail("No image could be extracted from the page")

    delete_current_conversation()
    cleanup()


if __name__ == "__main__":
    # Clean up on Ctrl+C
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(1)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(1)))

    parser = argparse.ArgumentParser(description="Generate image via Gemini web UI")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    generate(prompt=args.prompt, output=args.output)
