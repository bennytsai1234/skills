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
import atexit

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
_we_started_chrome = False

# ---------------------------------------------------------------------------
# Stale process cleanup (WSL-critical)
# ---------------------------------------------------------------------------

def _is_process_alive(pid):
    """Check if a process with given PID is still running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _kill_stale_xvfb():
    """Remove stale Xvfb lock files and kill orphaned Xvfb processes."""
    for n in range(99, 130):
        lock = f"/tmp/.X{n}-lock"
        if not os.path.exists(lock):
            continue
        try:
            with open(lock, "r") as f:
                pid = int(f.read().strip())
            if _is_process_alive(pid):
                # Check if it's actually an Xvfb process
                try:
                    cmdline = open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8", errors="replace")
                    if "Xvfb" not in cmdline:
                        # Not Xvfb — just remove stale lock
                        os.remove(lock)
                        xauth = f"/tmp/.X{n}-lock"  # already handled
                        continue
                except (FileNotFoundError, PermissionError):
                    pass
            else:
                # Process is dead — remove stale lock
                os.remove(lock)
                print(f"  Removed stale lock: {lock}", file=sys.stderr)
        except (ValueError, FileNotFoundError, PermissionError):
            try:
                os.remove(lock)
            except OSError:
                pass


def _kill_our_orphan_chrome():
    """Kill google-chrome processes using our profile dir that we don't own."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"--user-data-dir={PROFILE_DIR}"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                pid = int(line.strip())
                if pid != os.getpid():
                    print(f"  Killing orphan Chrome PID {pid}", file=sys.stderr)
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except OSError:
                        pass
            time.sleep(1)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Xvfb
# ---------------------------------------------------------------------------

def _find_free_display():
    """Find a free X display number, checking both lock files and live processes."""
    for n in range(99, 130):
        lock = f"/tmp/.X{n}-lock"
        if os.path.exists(lock):
            # Check if the process behind the lock is alive
            try:
                with open(lock, "r") as f:
                    pid = int(f.read().strip())
                if _is_process_alive(pid):
                    continue  # Display is genuinely in use
                else:
                    # Stale lock — remove it
                    os.remove(lock)
                    print(f"  Cleaned stale display lock :{n}", file=sys.stderr)
            except (ValueError, FileNotFoundError, PermissionError):
                try:
                    os.remove(lock)
                except OSError:
                    continue
        return n
    raise RuntimeError("No free X display found in range :99-:129")


def start_xvfb():
    global _xvfb_proc, _display
    display_num = _find_free_display()
    _display = f":{display_num}"
    _xvfb_proc = subprocess.Popen(
        ["Xvfb", _display, "-screen", "0", "1280x900x24", "-ac"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Verify Xvfb actually started (not just sleep and hope)
    deadline = time.time() + 5
    while time.time() < deadline:
        lock = f"/tmp/.X{display_num}-lock"
        if os.path.exists(lock) and _xvfb_proc.poll() is None:
            return _display
        time.sleep(0.3)

    # Xvfb may have crashed — check
    if _xvfb_proc.poll() is not None:
        raise RuntimeError(f"Xvfb failed to start on display {_display}")

    return _display


def stop_xvfb():
    global _xvfb_proc
    if _xvfb_proc:
        _xvfb_proc.terminate()
        try:
            _xvfb_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _xvfb_proc.kill()
            _xvfb_proc.wait(timeout=3)
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
    global _chrome_proc, _we_started_chrome

    for lock in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        p = os.path.join(PROFILE_DIR, lock)
        try:
            if os.path.exists(p) or os.path.islink(p):
                os.remove(p)
        except OSError:
            pass

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
            "--disable-gpu",
            f"--user-data-dir={PROFILE_DIR}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    _we_started_chrome = True

    deadline = time.time() + 20
    while time.time() < deadline:
        if _chrome_proc.poll() is not None:
            print("ERROR: Chrome process exited unexpectedly", file=sys.stderr)
            cleanup()
            sys.exit(1)
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
    global _chrome_proc, _we_started_chrome
    if _chrome_proc and _we_started_chrome:
        _chrome_proc.terminate()
        try:
            _chrome_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _chrome_proc.kill()
            try:
                _chrome_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass
        _chrome_proc = None


def cleanup():
    stop_chrome()
    stop_xvfb()


# Register atexit so cleanup always runs even on unhandled exceptions
atexit.register(cleanup)

# ---------------------------------------------------------------------------
# agent-browser helpers
# ---------------------------------------------------------------------------

def run(cmd, timeout=30, ignore_errors=False):
    full_cmd = ["agent-browser", "--session", SESSION_NAME] + cmd
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        if ignore_errors:
            return ""
        raise RuntimeError(f"agent-browser timed out after {timeout}s: {' '.join(cmd)}")
    if result.returncode != 0 and not ignore_errors:
        msg = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(msg or f"agent-browser failed: {' '.join(cmd)}")
    return result.stdout.strip()


def get_refs():
    out = run(["snapshot", "-i", "--json"], ignore_errors=True)
    if not out:
        return {}
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


def find_ref_contains(refs, include_terms, exclude_terms=None, role=None):
    exclude_terms = exclude_terms or []
    for k, v in refs.items():
        name = v.get("name", "")
        if role and v.get("role") != role:
            continue
        lowered = name.lower()
        if not any(term.lower() in lowered for term in include_terms):
            continue
        if any(term.lower() in lowered for term in exclude_terms):
            continue
        return k
    return None


def get_body_text():
    return run(["eval", "document.body ? document.body.innerText.slice(0,2000) : ''"],
               ignore_errors=True)


def has_generated_image_candidate():
    js = r"""
(() => {
  const imgs = [...document.querySelectorAll('img')];
  return imgs.some(img => {
    const src = img.currentSrc || img.src || '';
    const w = img.naturalWidth || img.width || 0;
    const h = img.naturalHeight || img.height || 0;
    if (w < 200 || h < 200) return false;
    if (/avatar|profile|googleusercontent.*photo/i.test(src)) return false;
    return src.startsWith('blob:') || src.startsWith('data:image/') || /googleusercontent\.com/.test(src);
  });
})()
"""
    out = run(["eval", js], ignore_errors=True)
    return out.strip().lower() == "true"


def fail(message):
    body = get_body_text()
    url = run(["get", "url"], ignore_errors=True)
    print(f"ERROR: {message}", file=sys.stderr)
    if url:
        print(f"URL: {url}", file=sys.stderr)
    snippet = re.sub(r"\s+", " ", body)[:400]
    if snippet:
        print(f"Page: {snippet}", file=sys.stderr)
    cleanup()
    sys.exit(1)


def _read_profile_prefs():
    prefs_path = os.path.join(PROFILE_DIR, "Default", "Preferences")
    try:
        with open(prefs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_download_dirs(output_path=None):
    dirs = []
    prefs = _read_profile_prefs()
    default_dir = prefs.get("download", {}).get("default_directory")
    if default_dir:
        dirs.append(os.path.expanduser(default_dir))

    dirs.append(os.path.expanduser("~/Downloads"))
    if output_path:
        dirs.append(os.path.dirname(os.path.abspath(output_path)))

    seen = set()
    unique_dirs = []
    for d in dirs:
        if not d or d in seen:
            continue
        seen.add(d)
        unique_dirs.append(d)
    return unique_dirs


def _normalize_googleusercontent_url(url):
    if not url:
        return None
    url = url.strip()
    if "=s1024-rj?" in url:
        return url.replace("=s1024-rj?", "=s0?")
    if "=s1024-rj" in url:
        return url.replace("=s1024-rj", "=s0")
    return re.sub(r"=s\d+[^?]*", "=s0", url)


def _extract_voyager_source_url():
    js = r"""
(() => {
  const resources = performance.getEntriesByType('resource')
    .filter(r => /lh3\.googleusercontent\.com\/gg-dl\//.test(r.name))
    .map(r => ({url: r.name, startTime: r.startTime || 0}))
    .sort((a, b) => a.startTime - b.startTime);
  if (resources.length) return resources[resources.length - 1].url;

  const imgs = [...document.querySelectorAll('img')]
    .filter(img => {
      const src = img.currentSrc || img.src || '';
      const inGenerated = img.closest('generated-image, .generated-image-container');
      return inGenerated && /googleusercontent\.com/.test(src);
    })
    .map(img => img.currentSrc || img.src || '');
  return imgs.length ? imgs[imgs.length - 1] : '';
})()
"""
    raw = run(["eval", js], timeout=30, ignore_errors=True)
    if not raw:
        return None
    try:
        url = json.loads(raw)
    except Exception:
        url = raw.strip().strip('"')
    return _normalize_googleusercontent_url(url)


def _fetch_voyager_bytes(url):
    js = r"""
(async function(url) {
  async function fetchBinary(u, hopsLeft) {
    if (!u || hopsLeft < 0) {
      return {error: 'no url'};
    }

    const resp = await fetch(u, {
      credentials: 'include',
      redirect: 'follow',
      cache: 'no-store',
    });

    const contentType = (resp.headers.get('content-type') || '').toLowerCase();
    const ab = await resp.arrayBuffer();
    const bytes = new Uint8Array(ab);

    let text = null;
    if (contentType.startsWith('text/plain')) {
      text = new TextDecoder().decode(bytes).trim();
    } else if (bytes.length > 8) {
      const prefix = new TextDecoder().decode(bytes.slice(0, 8)).trim();
      if (prefix.startsWith('http://') || prefix.startsWith('https://')) {
        text = new TextDecoder().decode(bytes).trim();
      }
    }

    if (text && (text.startsWith('http://') || text.startsWith('https://'))) {
      return fetchBinary(text, hopsLeft - 1);
    }

    let binary = '';
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    return {
      b64: btoa(binary),
      contentType,
      size: bytes.length,
    };
  }

  try {
    return JSON.stringify(await fetchBinary(url, 3));
  } catch (e) {
    return JSON.stringify({error: String(e)});
  }
})(%s)
""" % json.dumps(url)

    raw = run(["eval", js, "--json"], timeout=90, ignore_errors=True)
    if not raw:
        return None
    try:
        outer = json.loads(raw)
        inner = outer.get("data", {}).get("result", "{}")
        parsed = json.loads(inner)
    except Exception:
        return None

    if parsed.get("error") or not parsed.get("b64"):
        return None

    return base64.b64decode(parsed["b64"])


def wait_for_downloaded_image(start_ts, output_path, timeout=90):
    exts = (".png", ".jpg", ".jpeg", ".webp")
    dirs = get_download_dirs(output_path)
    deadline = time.time() + timeout
    last_pending = None

    while time.time() < deadline:
        newest = None
        for d in dirs:
            if not os.path.isdir(d):
                continue
            try:
                for name in os.listdir(d):
                    path = os.path.join(d, name)
                    if not os.path.isfile(path):
                        continue
                    lower = name.lower()
                    mtime = os.path.getmtime(path)
                    if lower.endswith(".crdownload") and mtime >= start_ts:
                        last_pending = path
                    if lower.endswith(exts) and mtime >= start_ts:
                        if newest is None or mtime > newest[0]:
                            newest = (mtime, path)
            except OSError:
                continue

        if newest:
            src = newest[1]
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            if os.path.abspath(src) != os.path.abspath(output_path):
                if os.path.exists(output_path):
                    os.remove(output_path)
                shutil.move(src, output_path)
            size_kb = os.path.getsize(output_path) // 1024
            print(f"\u2713 Saved: {output_path}")
            print(f"Size: {size_kb} KB")
            return True

        time.sleep(1)

    if last_pending:
        print(f"  Download still pending: {last_pending}", file=sys.stderr)
    return False


def download_image_via_voyager(output_path):
    refs = get_refs()
    download_ref = (
        find_ref(refs, "\u4e0b\u8f09\u539f\u5c3a\u5bf8\u5716\u7247")
        or find_ref(refs, "original", "image")
        or find_ref(refs, "download", "image")
    )

    if not download_ref:
        return False

    print("Downloading original image via Voyager...", file=sys.stderr)
    start_ts = time.time()
    run(["click", f"@{download_ref}"], timeout=30, ignore_errors=True)

    url = _extract_voyager_source_url()
    if url:
        try:
            data = _fetch_voyager_bytes(url)
            if data:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(data)
                size_kb = len(data) // 1024
                print(f"\u2713 Saved: {output_path}")
                print(f"Size: {size_kb} KB")
                return True
        except Exception as e:
            print(f"  Voyager URL fetch failed: {e}", file=sys.stderr)

    if wait_for_downloaded_image(start_ts, output_path, timeout=90):
        return True

    print("  Voyager download did not produce a file in time", file=sys.stderr)
    return False


def extract_image_via_js(output_path):
    """
    Extract the generated image from the page using fetch() on blob URLs.
    Falls back to canvas if fetch fails.
    Returns True if successful.
    """
    js = """
(async function() {
  const candidates = [];

  document.querySelectorAll('img[src^="blob:"]').forEach(img => {
    if ((img.naturalWidth || img.width) > 50) candidates.push(img);
  });

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
    try:
        result = subprocess.run(
            ["agent-browser", "--session", SESSION_NAME, "eval", js, "--json"],
            capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        print("  JS extraction timed out", file=sys.stderr)
        return False

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
        print(f"\u2713 Saved: {path}")
        print(f"Size: {size_kb} KB ({img['w']}x{img['h']})")
        saved.append(path)

    return bool(saved)

# ---------------------------------------------------------------------------
# Delete current conversation
# ---------------------------------------------------------------------------

def reset_to_new_conversation():
    """Navigate to a fresh Gemini page so next run starts clean."""
    print("Resetting to new conversation...", file=sys.stderr)
    try:
        run(["open", "https://gemini.google.com/app"], timeout=15, ignore_errors=True)
        run(["wait", "--load", "domcontentloaded"], timeout=15, ignore_errors=True)
        print("\u2713 Ready for next run", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: Reset failed (non-critical): {e}", file=sys.stderr)

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

    # WSL fix: clean up orphaned processes from previous crashed runs
    print("Cleaning up stale processes...", file=sys.stderr)
    _kill_stale_xvfb()
    _kill_our_orphan_chrome()

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

    # Connect session (reset first to avoid stale session state)
    subprocess.run(
        ["agent-browser", "--session", SESSION_NAME, "disconnect"],
        capture_output=True, timeout=10,
    )
    time.sleep(0.5)
    conn_result = subprocess.run(
        ["agent-browser", "--session", SESSION_NAME, "connect", str(port)],
        capture_output=True, text=True, timeout=15,
    )
    if conn_result.returncode != 0:
        err = (conn_result.stderr or conn_result.stdout or "").strip()
        print(f"ERROR: agent-browser connect failed: {err}", file=sys.stderr)
        cleanup()
        sys.exit(1)

    # Load Gemini with retry on network errors
    print("Opening Gemini...", file=sys.stderr)
    loaded = False
    for attempt in range(3):
        run(["open", "https://gemini.google.com/app"], timeout=30, ignore_errors=True)
        run(["wait", "--load", "domcontentloaded"], timeout=30, ignore_errors=True)
        time.sleep(4)

        body = get_body_text()
        url = run(["get", "url"], ignore_errors=True)

        if "\u7db2\u969b\u7db2\u8def" in body or "internet" in body.lower() or "connection" in body.lower():
            print(f"  Network error on attempt {attempt+1}, retrying...", file=sys.stderr)
            time.sleep(3)
            continue

        if "signin" in url.lower() or "\u767b\u5165" in body or "sign in" in body.lower():
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
        fail("Cannot load Gemini after 3 attempts \u2014 check network connection")

    refs = get_refs()

    # Strategy: type prompt directly in the main chat input.
    # Gemini auto-detects image generation requests from text.
    # This avoids the style picker that appears when clicking "建立圖像".
    print("Submitting prompt via chat input...", file=sys.stderr)

    # Find the main textbox
    textbox = None
    for k, v in refs.items():
        if v.get("role") == "textbox":
            textbox = k
            break
    if not textbox:
        fail("Cannot find text input")

    # Prefix prompt to ensure Gemini enters image generation mode
    full_prompt = f"Generate an image: {prompt}"
    run(["fill", f"@{textbox}", full_prompt])
    time.sleep(0.5)

    refs = get_refs()
    send_btn = find_ref_contains(
        refs,
        include_terms=["\u50b3\u9001\u8a0a\u606f", "\u53d1\u9001\u6d88\u606f", "send message", "send", "submit"],
        role="button",
    )
    if send_btn:
        run(["click", f"@{send_btn}"])
    else:
        run(["press", "Enter"])

    # Wait for generation
    print("Waiting for image generation...", file=sys.stderr)
    start_time = time.time()
    deadline = start_time + 180
    done = False
    while time.time() < deadline:
        time.sleep(4)
        refs = get_refs()
        names = {v.get("name", "") for v in refs.values()}

        has_stop = any("\u505c\u6b62\u56de\u8986" in n or "Stop" in n for n in names)
        has_download = any("\u4e0b\u8f09" in n or "download" in n.lower() for n in names)
        has_error = any("\u7121\u6cd5" in n or "\u932f\u8aa4" in n for n in names)
        generating = any("Creating" in n or "Generating" in n for n in names)
        has_image = has_generated_image_candidate()

        elapsed = int(time.time() - start_time)
        print(
            f"  [{elapsed}s] stop={has_stop} download={has_download} generating={generating} image={has_image}",
            file=sys.stderr,
        )

        if has_error:
            fail("Gemini reported an error")

        if has_download:
            print("  \u2192 Download button detected!", file=sys.stderr)
            done = True
            break

        if has_image and not has_stop:
            print("  \u2192 Generated image detected on page", file=sys.stderr)
            done = True
            break

    if not done:
        fail("Image generation timed out after 180s")

    # Build output path
    ts = int(time.time())
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt[:30]).strip("-")
    if not output:
        output = f"/tmp/gemini-img-{slug}-{ts}.png"

    time.sleep(1)
    ok = download_image_via_voyager(output)
    if not ok:
        print("Falling back to page image extraction...", file=sys.stderr)
        ok = extract_image_via_js(output)

    if not ok:
        fail("No image could be extracted from the page")

    reset_to_new_conversation()
    cleanup()


if __name__ == "__main__":
    def _signal_handler(signum, frame):
        cleanup()
        sys.exit(1)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    parser = argparse.ArgumentParser(description="Generate image via Gemini web UI")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()

    try:
        generate(prompt=args.prompt, output=args.output)
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: Unhandled exception: {e}", file=sys.stderr)
        cleanup()
        sys.exit(1)
