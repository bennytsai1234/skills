#!/usr/bin/env python3
"""
One-shot Gemini image generation using Playwright Node API.
Avoids playwright-cli session persistence issues under Xvfb.
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap

PROFILE_DIR = os.path.expanduser("~/.cache/skills/image-generate/gemini-profile")
PLAYWRIGHT_PATH = "/home/benny/.nvm/versions/node/v24.14.1/lib/node_modules/@playwright/cli/node_modules/playwright"
XVFB_PROC = None


def ensure_display():
    global XVFB_PROC
    if os.environ.get("DISPLAY"):
        return
    if not shutil.which("Xvfb"):
        raise RuntimeError("No DISPLAY found and Xvfb is not installed")
    display = ":99"
    lock_path = "/tmp/.X99-lock"
    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
        except OSError:
            pass
    XVFB_PROC = subprocess.Popen(
        ["Xvfb", display, "-ac", "-screen", "0", "1280x800x24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    os.environ["DISPLAY"] = display
    import time
    time.sleep(1.5)
    if XVFB_PROC.poll() is not None:
        XVFB_PROC = None
        raise RuntimeError("Xvfb failed to start")


def cleanup():
    global XVFB_PROC
    if XVFB_PROC is not None:
        try:
            XVFB_PROC.terminate()
            XVFB_PROC.wait(timeout=3)
        except Exception:
            try:
                XVFB_PROC.kill()
            except Exception:
                pass
        XVFB_PROC = None


def generate(prompt: str, output: str | None):
    ensure_display()
    os.makedirs(PROFILE_DIR, exist_ok=True)
    if not output:
        output = "/tmp/gemini-generated-image.png"
    output = os.path.abspath(output)

    js = textwrap.dedent(
        r'''
        const fs = require('fs');
        const path = require('path');
        const { chromium } = require(%(playwright_path)r);

        const prompt = %(prompt)r;
        const output = %(output)r;
        const profileDir = %(profile)r;

        const sleep = ms => new Promise(r => setTimeout(r, ms));

        async function bodyText(page) {
          try {
            return await page.evaluate(() => document.body ? document.body.innerText.slice(0, 4000) : '');
          } catch {
            return '';
          }
        }

        async function waitForGemini(page) {
          console.error('Opening Gemini via Google Search (avoids 502)...');
          await page.goto('https://www.google.com/search?q=gemini+ai+chat', { waitUntil: 'domcontentloaded', timeout: 45000 });
          await sleep(2000);
          const clicked = await page.evaluate(() => {
            const links = [...document.querySelectorAll('a[href*="gemini.google.com"]')];
            if (links.length) { links[0].click(); return links[0].href; }
            return null;
          });
          if (!clicked) {
            await page.goto('https://gemini.google.com/app', { waitUntil: 'domcontentloaded', timeout: 45000 });
          }
          for (let i = 0; i < 8; i++) {
            await sleep(5000);
            const url = page.url();
            const body = await bodyText(page);
            const is502 = body.includes('502') && /error/i.test(body);
            console.error(`  [${i+1}/8] url=${url.slice(0,60)} 502=${is502}`);
            if (url.includes('gemini.google.com') && !is502) return;
            if (is502 && url.includes('gemini.google.com')) await page.reload({ waitUntil: 'domcontentloaded' });
          }
          throw new Error('Could not load Gemini after navigating from Google Search');
        }

        async function submitPrompt(page) {
          const editor = '.ql-editor';
          await page.waitForSelector(editor, { timeout: 45000 });
          await page.click(editor);
          await page.fill(editor, `Generate an image: ${prompt}`);
          await page.keyboard.press('Enter');
          console.error('Waiting for image generation...');
        }

        async function waitForImage(page) {
          const deadline = Date.now() + 180000;
          while (Date.now() < deadline) {
            await sleep(4000);
            const info = await page.evaluate(() => {
              const text = document.body ? document.body.innerText.slice(0, 3000) : '';
              const imgs = [...document.querySelectorAll('img')];
              const candidate = imgs.find(img => {
                const src = img.currentSrc || img.src || '';
                const w = img.naturalWidth || img.width || 0;
                const h = img.naturalHeight || img.height || 0;
                if (w < 200 || h < 200) return false;
                if (/avatar|profile|googleusercontent.*photo/i.test(src)) return false;
                return src.startsWith('blob:') || src.startsWith('data:image/') || /googleusercontent\.com/.test(src);
              });
              return {
                hasStop: text.includes('停止回覆') || text.includes('Stop responding'),
                generating: text.includes('Creating') || text.includes('Generating') || text.includes('建立中'),
                hasError: text.includes('無法完成') || text.includes('遇到問題'),
                is502: text.includes('502') && /error/i.test(text),
                found: !!candidate,
              };
            });
            console.error(`  generating=${info.generating} image=${info.found} 502=${info.is502}`);
            if (info.is502) {
              await page.reload({ waitUntil: 'domcontentloaded' });
              continue;
            }
            if (info.hasError) throw new Error('Gemini reported an error');
            if (info.found && !info.hasStop) return;
          }
          throw new Error('Image generation timed out after 180s');
        }

        async function saveImage(page) {
          console.error('Extracting image from page...');
          const data = await page.evaluate(async () => {
            const imgs = [...document.querySelectorAll('img')];
            const candidates = imgs.filter(img => {
              const src = img.currentSrc || img.src || '';
              const w = img.naturalWidth || img.width || 0;
              const h = img.naturalHeight || img.height || 0;
              if (w < 200 || h < 200) return false;
              if (/avatar|profile|googleusercontent.*photo/i.test(src)) return false;
              return src.startsWith('blob:') || src.startsWith('data:image/') || src.startsWith('https://');
            });
            if (!candidates.length) return { error: 'no image candidates found' };
            const img = candidates[candidates.length - 1];
            try {
              const resp = await fetch(img.src, { credentials: 'include' });
              const blob = await resp.blob();
              const ab = await blob.arrayBuffer();
              const arr = new Uint8Array(ab);
              let s = '';
              for (let i = 0; i < arr.length; i++) s += String.fromCharCode(arr[i]);
              return { b64: btoa(s), type: blob.type || 'image/png', w: img.naturalWidth||img.width, h: img.naturalHeight||img.height };
            } catch (e) {
              const c = document.createElement('canvas');
              c.width = img.naturalWidth || img.width;
              c.height = img.naturalHeight || img.height;
              c.getContext('2d').drawImage(img, 0, 0);
              const url = c.toDataURL('image/png');
              return { b64: url.split(',')[1], type: 'image/png', w: c.width, h: c.height };
            }
          });
          if (!data || data.error || !data.b64) throw new Error(data?.error || 'failed to extract image');
          fs.mkdirSync(path.dirname(output), { recursive: true });
          fs.writeFileSync(output, Buffer.from(data.b64, 'base64'));
          const sizeKb = Math.floor(fs.statSync(output).size / 1024);
          console.log(`✓ Saved: ${output}`);
          console.log(`Size: ${sizeKb} KB (${data.w}x${data.h})`);
        }

        (async () => {
          const context = await chromium.launchPersistentContext(profileDir, {
            headless: false,
            channel: 'chrome',
            viewport: { width: 1440, height: 900 },
            args: ['--no-sandbox', '--disable-dev-shm-usage'],
          });
          try {
            const page = context.pages()[0] || await context.newPage();
            await waitForGemini(page);
            const body = await bodyText(page);
            if ((/signin|sign in/i.test(body) || body.includes('登入')) && !body.includes('Gemini')) {
              throw new Error('Not logged in to Gemini. Login once manually with the saved profile.');
            }
            await submitPrompt(page);
            await waitForImage(page);
            await saveImage(page);
          } finally {
            await context.close();
          }
        })().catch(err => {
          console.error('ERROR: ' + (err && err.stack ? err.stack : String(err)));
          process.exit(1);
        });
        ''' % {
            "playwright_path": PLAYWRIGHT_PATH,
            "prompt": prompt,
            "output": output,
            "profile": PROFILE_DIR,
        }
    )

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(js)
        script_path = f.name

    try:
        result = subprocess.run(
            ["node", script_path],
            text=True,
            capture_output=True,
            timeout=240,
            env=os.environ.copy(),
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.returncode != 0:
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="")
            raise RuntimeError("gemini image generation failed")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
    finally:
        try:
            os.remove(script_path)
        except OSError:
            pass


def _signal_handler(signum, frame):
    cleanup()
    sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    parser = argparse.ArgumentParser(description="Generate image via Gemini web UI")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()

    try:
        generate(prompt=args.prompt, output=args.output)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        cleanup()
        sys.exit(1)
    finally:
        cleanup()
