#!/usr/bin/env python3
"""
video-to-text — 把影片網址轉成帶時間戳的繁體中文逐字稿。

流程：
    1. yt-dlp 抓影片資訊，並嘗試抓現成字幕（SRT）
    2. 沒字幕才下載音訊，交給 MOSS-Transcribe-Diarize 辨識
    3. OpenCC s2twp 轉台灣正體
    4. 輸出 .txt

兩條路徑（字幕／辨識）都會產生同一種 Segment 結構，所以時間戳格式一致，
下游只需要一個 formatter。

以 YouTube 為主要目標；B 站／抖音能跑就跑，不特別保證。
"""

import os
import re
import sys
import time
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

# ------------------------------------------------------------
#  設定
# ------------------------------------------------------------
OUTPUT_DIR = Path.home() / "video-transcripts"
MODEL_ID = "OpenMOSS-Team/MOSS-Transcribe-Diarize"
OPENCC_CONFIG = "s2twp"          # 台灣正體，含「視頻→影片」等慣用詞
SUB_LANGS = "zh-TW,zh-Hant,zh,zh-Hans,zh-CN,zh-Hant-.*,zh-Hans-.*,en,en-.*"
KEEP_AUDIO = False
CHUNK_SECONDS = 60               # 切片上限；實測 60s 的 RTF 最佳（見 transcribe_audio）
SILENCE_DB = -35                 # silencedetect 的靜音門檻（dB）
SILENCE_MIN_S = 0.35             # 至少多長才算一個可切的靜音
MAX_NEW_TOKENS = 4096            # 單一 chunk 的輸出上限，60s 語音綽綽有餘

# 這台 WSL 的 /tmp 是 3.9G tmpfs，大型模型的暫存會塞爆它 → 一律改指到家目錄
os.environ.setdefault("TMPDIR", str(Path.home() / ".cache" / "pip-tmp"))


# ------------------------------------------------------------
#  0. 確保跑在自己的 venv 裡
# ------------------------------------------------------------
def ensure_venv():
    """腳本可能被系統 python 直接呼叫，但依賴裝在 .venv，這裡自動接管。"""
    venv_py = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
    if sys.prefix == sys.base_prefix and venv_py.exists():
        os.execv(str(venv_py), [str(venv_py), str(Path(__file__).resolve()), *sys.argv[1:]])


ensure_venv()


@dataclass
class Segment:
    start: float          # 秒
    end: float            # 秒
    speaker: str | None   # 'S01' 之類；抓字幕時為 None
    text: str


# ------------------------------------------------------------
#  1. 環境檢查
# ------------------------------------------------------------
def check_environment(need_asr: bool):
    missing = []
    for exe, hint in (("yt-dlp", "pip install -U yt-dlp"),
                      ("ffmpeg", "sudo apt install ffmpeg")):
        if not shutil.which(exe):
            missing.append(f"  {exe:10s} → {hint}")
    if need_asr:
        try:
            import moss_transcribe_diarize  # noqa: F401
        except ImportError:
            missing.append("  MOSS       → 見 SKILL.md「環境建置」")
    if missing:
        print("✗ 缺少依賴：", *missing, sep="\n")
        sys.exit(1)


# ------------------------------------------------------------
#  2. 影片資訊
# ------------------------------------------------------------
def get_video_info(url):
    r = subprocess.run(["yt-dlp", "--dump-json", "--no-warnings", url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("✗ 取得影片資訊失敗：")
        print(r.stderr.strip()[:800])
        sys.exit(1)
    d = json.loads(r.stdout)
    return {
        "title": d.get("title") or "untitled",
        "uploader": d.get("uploader") or "",
        "duration": d.get("duration") or 0,
        "id": d.get("id") or "",
        "url": d.get("webpage_url") or url,
        "has_subs": bool(d.get("subtitles")),
        "has_auto": bool(d.get("automatic_captions")),
    }


def safe_filename(name):
    name = re.sub(r'[\\/:*?"<>|\n\r\t]', "_", name).strip()
    return (name[:120] or "transcript")


# ------------------------------------------------------------
#  3. 路徑 A：抓現成字幕
# ------------------------------------------------------------
def fetch_subtitles(url, workdir):
    """先試人工字幕，再試自動字幕。回傳 (segments, 來源說明) 或 (None, None)。"""
    for flag, label in ((["--write-subs"], "人工字幕"),
                        (["--write-auto-subs"], "自動字幕")):
        for f in Path(workdir).glob("sub*"):
            f.unlink()
        subprocess.run(
            ["yt-dlp", "--skip-download", *flag,
             "--sub-langs", SUB_LANGS, "--sub-format", "vtt/srt/best",
             "--convert-subs", "srt", "-o", os.path.join(workdir, "sub"),
             "--no-warnings", url],
            capture_output=True, text=True)
        srts = list(Path(workdir).glob("sub*.srt"))
        if srts:
            best = pick_best_srt(srts)
            segs = parse_srt(best.read_text(encoding="utf-8", errors="ignore"))
            if segs:
                lang = best.stem.split(".", 1)[-1]
                return segs, f"{label}（{lang}）"
    return None, None


def pick_best_srt(paths):
    """yt-dlp 會把所有符合的語言都抓下來，這裡依 SUB_LANGS 的偏好序挑一個。

    不能用檔名字母序 —— 那會讓 'sub.zh-Hans.srt' 贏過 'sub.zh-TW.srt'，
    等於放著現成的繁體不用，改走「繁→簡→繁」的來回轉換。
    """
    prefs = [p.strip() for p in SUB_LANGS.split(",")]

    def rank(path):
        lang = path.stem.split(".", 1)[-1] if "." in path.stem else ""
        for i, pref in enumerate(prefs):
            if re.fullmatch(pref.replace(".*", ".*"), lang, re.IGNORECASE):
                return i
        return len(prefs)

    return min(paths, key=rank)


_TS = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*"
                 r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


def parse_srt(raw):
    """SRT → [Segment]。只剝掉序號與內嵌標記，時間戳保留。"""
    segs = []
    blocks = re.split(r"\n\s*\n", raw.strip())
    for blk in blocks:
        lines = [ln for ln in blk.splitlines() if ln.strip()]
        if not lines:
            continue
        if re.fullmatch(r"\d+", lines[0].strip()):   # 序號行
            lines = lines[1:]
        if not lines:
            continue
        m = _TS.search(lines[0])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = " ".join(lines[1:])
        text = re.sub(r"<[^>]+>", "", text).strip()   # <c>、<00:00:00.000>
        if text:
            segs.append(Segment(start, end, None, text))
    return segs


# ------------------------------------------------------------
#  4. 路徑 B：語音辨識（MOSS-Transcribe-Diarize）
# ------------------------------------------------------------
def download_audio(url, workdir):
    out = os.path.join(workdir, "audio.%(ext)s")
    r = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", "-o", out, "--no-warnings", url],
        capture_output=True, text=True)
    if r.returncode != 0:
        print("✗ 音訊下載失敗：")
        print(r.stderr.strip()[:800])
        sys.exit(1)
    mp3s = list(Path(workdir).glob("audio*.mp3"))
    if not mp3s:
        print("✗ 音訊下載後找不到檔案")
        sys.exit(1)
    return str(mp3s[0])


def find_silences(audio_path):
    """用 ffmpeg silencedetect 找出所有靜音區間，回傳 [(start_s, end_s), ...]。

    刻意不用 funasr 的 fsmn-vad：匯入 funasr 會全域改寫 huggingface_hub，
    把後續所有模型下載導向 ModelScope，導致 MOSS 從 HF 抓不到（404）。
    silencedetect 已內建於 ffmpeg，不下載模型、不碰 hub，這裡也夠用。
    """
    r = subprocess.run(
        ["ffmpeg", "-i", audio_path, "-af",
         f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN_S}", "-f", "null", "-"],
        capture_output=True, text=True)
    sils, start = [], None
    for m in re.finditer(r"silence_(start|end): ([0-9.]+)", r.stderr):
        if m.group(1) == "start":
            start = float(m.group(2))
        elif start is not None:
            sils.append((start, float(m.group(2))))
            start = None
    return sils


def plan_chunks(audio_path, duration, max_chunk_s=CHUNK_SECONDS):
    """規劃切點，回傳 [(start_s, end_s), ...]。

    切點只落在靜音的中點，所以不會切斷任何一個字。若某段連續語音超過
    max_chunk_s（有人一口氣講很久），寧可讓該 chunk 長一點也要等到下一個
    靜音才切 —— 最多放寬到 2 倍；真的還是找不到才硬切。
    """
    cuts = [(a + b) / 2 for a, b in find_silences(audio_path)]
    if not cuts:
        return [(0.0, duration)]

    chunks, pos = [], 0.0
    while pos < duration - 0.5:
        limit = pos + max_chunk_s
        avail = [c for c in cuts if c > pos + 5]
        inside = [c for c in avail if c <= limit]
        if inside:
            end = max(inside)                       # 限度內最靠後的切點
        elif avail and avail[0] <= pos + max_chunk_s * 2:
            end = avail[0]                          # 放寬，避免切在字中間
        else:
            end = min(limit, duration)              # 真的沒靜音才硬切
        end = min(end, duration)
        chunks.append((pos, end))
        pos = end
    return chunks


def slice_audio(audio_path, start, end, dest):
    """切出 [start, end) 這段，轉成 16k 單聲道 wav。"""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", audio_path,
         "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
         "-ar", "16000", "-ac", "1", dest],
        check=True, capture_output=True)
    return dest


# ╔══════════════════════════════════════════════════════════╗
# ║  ★ 可抽換模組：語音辨識引擎 ★                              ║
# ║  介面固定：傳入音訊檔路徑，回傳 [Segment]。                ║
# ║  換引擎只要改寫這個函式，其餘流程完全不動。               ║
# ╚══════════════════════════════════════════════════════════╝
def transcribe_audio(audio_path, duration=0):
    """MOSS-Transcribe-Diarize + VAD 切片。

    為什麼一定要切片：這個模型是自迴歸的 audio-LLM，KV cache 隨長度膨脹，
    整段餵進去的耗時是「超線性」的（實測 939s 音訊跑 18 分鐘還沒結束）。
    切成 60s 一段後回到線性，實測 RTF 約 0.47（60s 是甜蜜點，10s/120s 都較差）。
    模型只載入一次，所有 chunk 重複使用。
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoProcessor
    from moss_transcribe_diarize import parse_transcript
    from moss_transcribe_diarize.inference_utils import (
        build_transcription_messages, generate_transcription, resolve_device)

    chunks = plan_chunks(audio_path, duration)
    if not chunks:
        return []
    print(f"· 切出 {len(chunks)} 段（切點皆在靜音處）")

    device = resolve_device("auto")
    # sm_75（Turing）無 bf16 硬體單元，但 torch 會以軟體模擬，實測數值正常。
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, trust_remote_code=True, dtype="auto"
    ).to(dtype=dtype).to(device).eval()
    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

    out = []
    workdir = Path(audio_path).parent
    for i, (a, b) in enumerate(chunks, 1):
        piece = slice_audio(audio_path, a, b, str(workdir / f"chunk{i:03d}.wav"))
        result = generate_transcription(
            model, processor, build_transcription_messages(piece),
            max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            device=device, dtype=dtype)
        for s in parse_transcript(result["text"]):
            if s.text.strip():
                # chunk 內的時間戳是相對的，加回 chunk 起點還原成絕對時間
                out.append(Segment(s.start + a, s.end + a, s.speaker, s.text))
        os.unlink(piece)
        pct = i / len(chunks) * 100
        print(f"\r  辨識中 {i}/{len(chunks)} ({pct:.0f}%)", end="", flush=True)
    print()
    return out
# ────────────────  可抽換模組結束  ────────────────


# ------------------------------------------------------------
#  5. 簡轉繁
# ------------------------------------------------------------
def to_traditional(text):
    try:
        from opencc import OpenCC
        return OpenCC(OPENCC_CONFIG).convert(text)
    except Exception:
        r = subprocess.run(["opencc", "-c", OPENCC_CONFIG],
                           input=text, capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else text


# ------------------------------------------------------------
#  6. 輸出
# ------------------------------------------------------------
def fmt_ts(sec):
    sec = int(sec)
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def render(info, segs, source_kind):
    """輸出格式：每行一段，開頭一個絕對時間戳。

    刻意不輸出 MOSS 的講者標籤（S01/S02）：每個 chunk 是獨立辨識的，
    模型無從得知上一段的 S01 與這段的 S01 是不是同一人，跨 chunk 的編號
    因此沒有意義。實測獨白影片就被標出 158 個 S01 + 3 個 S02。
    錯的資料比沒有資料更糟，所以直接捨棄。
    """
    head = [
        f"# {info['title']}",
        f"來源：{info['url']}",
        f"頻道：{info['uploader']}｜時長：{fmt_ts(info['duration'])}｜取得方式：{source_kind}",
        "",
    ]
    body = [f"[{fmt_ts(s.start)}] {s.text}" for s in segs]
    return "\n".join(head + body) + "\n"


# ------------------------------------------------------------
#  主流程
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("用法：transcribe.py <影片網址>")
        sys.exit(1)
    url = sys.argv[1]
    t_start = time.time()

    check_environment(need_asr=False)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    info = get_video_info(url)
    print(f"▸ {info['title']}")
    print(f"  {info['uploader']}｜{fmt_ts(info['duration'])}")

    with tempfile.TemporaryDirectory(prefix="v2t-") as workdir:
        segs, kind = fetch_subtitles(url, workdir)

        if segs:
            print(f"✓ 取得{kind}（{len(segs)} 段），跳過語音辨識")
        else:
            print("· 無現成字幕，改用語音辨識")
            check_environment(need_asr=True)
            audio = download_audio(url, workdir)
            print(f"· 音訊已下載，開始辨識（模型 {MODEL_ID.split('/')[-1]}）…")
            segs = transcribe_audio(audio, info["duration"])
            kind = "語音辨識"
            if KEEP_AUDIO:
                shutil.copy(audio, OUTPUT_DIR / Path(audio).name)
            if not segs:
                print("✗ 辨識結果為空")
                sys.exit(1)
            print(f"✓ 辨識完成（{len(segs)} 段）")

    for s in segs:
        s.text = to_traditional(s.text)

    out = OUTPUT_DIR / f"{safe_filename(info['title'])}.txt"
    content = render(info, segs, kind)
    out.write_text(content, encoding="utf-8")

    chars = sum(len(s.text) for s in segs)
    el = time.time() - t_start
    rate = f"（{info['duration']/el:.1f}x 即時）" if info["duration"] and el else ""
    print(f"✓ 已輸出：{out}")
    print(f"  {len(segs)} 段、約 {chars} 字、取得方式：{kind}")
    print(f"  總耗時 {el/60:.1f} 分 {rate}")


if __name__ == "__main__":
    main()
