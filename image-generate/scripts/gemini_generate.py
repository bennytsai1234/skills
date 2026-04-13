#!/usr/bin/env python3
"""
Image generation via Gemini web UI using playwright-cli.
Usage: python3 gemini_generate.py --prompt "..." [--output path.png]
"""
import argparse
import subprocess
import sys
import os
import json
import time
import shutil
import re
import base64
import signal
import atexit

PROFILE_DIR = os.path.expanduser("~/.cache/skills/image-generate/gemini-profile")
SESSION_NAME = "gemini-img"

def run(cmd, timeout=30, ignore_errors=False, raw=False):
    full_cmd = ["playwright-cli", "-s", SESSION_NAME]
    if raw:
        full_cmd.append("--raw")
        
    if isinstance(cmd, str):
        full_cmd.append(cmd)
    else:
        full_cmd.extend(cmd)
        
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        if ignore_errors:
            return ""
        raise RuntimeError(f"playwright-cli timed out after {timeout}s: {' '.join(full_cmd)}")
    if result.returncode != 0 and not ignore_errors:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(err or f"playwright-cli failed: {' '.join(full_cmd)}")
    return result.stdout.strip()

def get_body_text():
    return run(["eval", "document.body ? document.body.innerText.slice(0,2000) : ''"], ignore_errors=True, raw=True)

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
    out = run(["eval", js], ignore_errors=True, raw=True)
    try:
        # Evaluate JSON string
        b = json.loads(out)
        if isinstance(b, str):
            out = b
    except:
        pass
    return out.strip().lower() == "true"

def fail(message):
    body = get_body_text()
    url = run(["eval", "window.location.href"], ignore_errors=True, raw=True)
    print(f"ERROR: {message}", file=sys.stderr)
    if url:
        print(f"URL: {url.strip('\"')}", file=sys.stderr)
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
    raw = run(["eval", js], timeout=30, ignore_errors=True, raw=True)
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

    raw = run(["eval", js], timeout=90, ignore_errors=True, raw=True)
    if not raw:
        return None
    try:
        try:
            outer = json.loads(raw)
            if isinstance(outer, str):
                outer = json.loads(outer)
            parsed = outer
        except Exception:
             return None
             
        if parsed.get("error") or not parsed.get("b64"):
            return None
        return base64.b64decode(parsed["b64"])
    except Exception:
        return None

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
    print("Downloading original image via Voyager...", file=sys.stderr)
    start_ts = time.time()
    # Click download original logic
    run(["eval", "document.evaluate('//button[contains(@aria-label, \"下載原尺寸圖片\") or contains(@title, \"下載原尺寸圖片\") or contains(@aria-label, \"Download\") or contains(@title, \"Download\")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()"], timeout=30, ignore_errors=True)

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
  if (!candidates.length) return {error: 'no images found'};
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
    ? {images: results}
    : {error: 'extraction failed for all candidates'};
})()
"""
    raw = run(["eval", js], timeout=60, ignore_errors=True, raw=True)
    if not raw:
        return False
    try:
        d = json.loads(raw)
        if isinstance(d, str):
            d = json.loads(d)
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
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        size_kb = len(data) // 1024
        print(f"\u2713 Saved: {path}")
        print(f"Size: {size_kb} KB ({img['w']}x{img['h']})")
        saved.append(path)
    return bool(saved)

def reset_to_new_conversation():
    print("Resetting to new conversation...", file=sys.stderr)
    try:
        run(["open", "https://gemini.google.com/app"], timeout=15, ignore_errors=True)
        print("\u2713 Ready for next run", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: Reset failed (non-critical): {e}", file=sys.stderr)

def cleanup():
    subprocess.run(["playwright-cli", "-s", SESSION_NAME, "close"], capture_output=True)

atexit.register(cleanup)

def generate(prompt, output):
    if not shutil.which("playwright-cli"):
        print("ERROR: playwright-cli not found. Ensure it is installed via npm install -g @playwright/cli", file=sys.stderr)
        sys.exit(1)

    # Make sure old session is clean
    cleanup()

    print("Opening Gemini via Google Search (avoids 502)...", file=sys.stderr)
    os.makedirs(PROFILE_DIR, exist_ok=True)
    try:
        # Open Google Search first — mimics what the user does manually:
        # type "gemini" in the address bar → click the first result.
        # Direct navigation to gemini.google.com/app gets 502 because Google
        # detects the missing Referer. Coming from google.com/search bypasses this.
        run(["open", "--headed", f"--profile={PROFILE_DIR}", "https://www.google.com/search?q=gemini+ai+chat"], timeout=45)
    except Exception as e:
        fail(f"Failed to open Browser: {e}")

    time.sleep(2)

    # Click the first Gemini result in Google Search
    js_click_gemini = r"""
(() => {
  const links = [...document.querySelectorAll('a[href*="gemini.google.com"]')];
  if (links.length) { links[0].click(); return 'clicked:' + links[0].href; }
  // fallback: look for any heading with "Gemini"
  const all = [...document.querySelectorAll('a')].filter(a => /gemini\.google\.com/.test(a.href));
  if (all.length) { all[0].click(); return 'clicked:' + all[0].href; }
  return 'not_found';
})()
"""
    result = run(["eval", js_click_gemini], timeout=15, ignore_errors=True, raw=True)
    print(f"  Search click result: {result}", file=sys.stderr)

    if "not_found" in (result or ""):
        # Fallback: navigate directly
        print("  Gemini link not found in search, navigating directly...", file=sys.stderr)
        run(["eval", "window.location.href='https://gemini.google.com/app'"], timeout=15, ignore_errors=True)

    # Wait for Gemini to load (may take a moment after click/redirect)
    print("  Waiting for Gemini to load...", file=sys.stderr)
    loaded = False
    for attempt in range(6):  # up to ~30s
        time.sleep(5)
        body = get_body_text()
        url = run(["eval", "window.location.href"], ignore_errors=True, raw=True).strip('"')
        is_502 = "502" in body and "error" in body.lower()
        on_gemini = "gemini.google.com" in url
        print(f"  [{attempt+1}/6] url={url[:60]} 502={is_502} on_gemini={on_gemini}", file=sys.stderr)
        if on_gemini and not is_502:
            loaded = True
            break
        if is_502 and on_gemini:
            # On Gemini but got 502 — reload once
            run(["eval", "window.location.reload()"], timeout=15, ignore_errors=True)
        elif not on_gemini:
            # Still on search page or redirecting — wait more
            pass

    if not loaded:
        fail("Could not load Gemini after navigating from Google Search. Try again.")

    if "signin" in body.lower() or "登入" in body or "sign in" in body.lower():
        if "Gemini" not in body:
            print(f"ERROR: Not logged in. Please log in manually by running:\n  playwright-cli open --profile={PROFILE_DIR} https://gemini.google.com/app", file=sys.stderr)
            cleanup()
            sys.exit(1)

    print("Submitting prompt via chat input...", file=sys.stderr)
    full_prompt = f"Generate an image: {prompt}"
    
    run(["fill", ".ql-editor", full_prompt, "--submit"])
    time.sleep(0.5)

    print("Waiting for image generation...", file=sys.stderr)
    start_time = time.time()
    deadline = start_time + 180
    done = False
    while time.time() < deadline:
        time.sleep(4)
        body = get_body_text()
        
        has_stop = "停止回覆" in body or "Stop responding" in body
        generating = "Creating" in body or "Generating" in body or "建立中" in body
        has_image = has_generated_image_candidate()
        is_502 = "502" in body and "error" in body.lower()
        has_error = "無法完成" in body or "遇到問題" in body

        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] stop={has_stop} generating={generating} image={has_image} 502={is_502}", file=sys.stderr)

        if is_502:
            # 502 mid-session: reload and let the loop continue waiting
            print("  502 mid-session, reloading page...", file=sys.stderr)
            run(["eval", "window.location.reload()"], timeout=30, ignore_errors=True)
            time.sleep(5)
            continue
        if has_error:
            fail("Gemini reported an error.")
        if has_image and not has_stop:
            print("  \u2192 Generated image detected on page", file=sys.stderr)
            done = True
            break
            
    if not done:
        fail("Image generation timed out after 180s")

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

    parser = argparse.ArgumentParser(description="Generate image via Gemini web UI using playwright-cli")
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
