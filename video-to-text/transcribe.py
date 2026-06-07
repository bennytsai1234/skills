#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video-to-text — 影片網址轉繁體中文純文字逐字稿

流程：解析網址 → 抓影片資訊 → 優先抓現成字幕 →（沒字幕才）語音辨識
      → 清洗文字 → 簡轉繁 → 輸出純文字 .txt

用法：
    python transcribe.py "<影片網址>"
"""

import os
import re
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

# ============================================================
#  設定區（常用參數都在這裡，可自行調整）
# ============================================================
OUTPUT_DIR = Path.home() / "video-transcripts"   # 逐字稿存放資料夾
WHISPER_MODEL = "medium"                          # 辨識模型：medium / small / base
KEEP_AUDIO = False                                # 是否保留下載的音訊
OPENCC_CONFIG = "s2twp"                           # 簡轉繁設定（台灣正體含慣用詞）
SUB_LANGS = "zh-Hant,zh-Hans,zh,zh-CN,zh-TW,zh-HK"  # 想抓的字幕語言（依序嘗試）
# ============================================================


# ------------------------------------------------------------
#  0. 環境檢查
# ------------------------------------------------------------
def check_environment():
    missing = []
    if shutil.which("yt-dlp") is None:
        missing.append("yt-dlp（pip install -U yt-dlp）")
    if shutil.which("ffmpeg") is None:
        missing.append("ffmpeg（sudo apt install ffmpeg）")
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        missing.append("faster-whisper（pip install faster-whisper）")
    try:
        import opencc  # noqa: F401
    except ImportError:
        missing.append("opencc（pip install opencc）")

    if missing:
        print("⚠ 以下依賴尚未安裝：")
        for m in missing:
            print(f"   - {m}")
        sys.exit(1)


# ------------------------------------------------------------
#  1~2. 解析網址、抓影片資訊
# ------------------------------------------------------------
def get_video_info(url):
    """用 yt-dlp 取得影片 metadata（標題、作者、時長、id）。"""
    cmd = ["yt-dlp", "--dump-single-json", "--no-warnings", "--skip-download", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠ 無法取得影片資訊：")
        print(result.stderr.strip())
        sys.exit(1)
    info = json.loads(result.stdout)
    return {
        "id": info.get("id", "video"),
        "title": info.get("title", "untitled"),
        "uploader": info.get("uploader", "未知作者"),
        "duration": info.get("duration", 0),
        "webpage_url": info.get("webpage_url", url),
    }


def safe_filename(name):
    """把標題清成合法檔名。"""
    name = re.sub(r'[\\/:*?"<>|\n\r\t]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:120] if len(name) > 120 else name


# ------------------------------------------------------------
#  3. 優先抓現成字幕
# ------------------------------------------------------------
def try_fetch_subtitles(url, workdir):
    """
    嘗試抓人工字幕；沒有則抓自動字幕。
    成功回傳清洗後的純文字，失敗回傳 None。
    """
    base = os.path.join(workdir, "sub")

    # 先試人工字幕，再試自動字幕
    for auto_flag in (["--write-subs"], ["--write-auto-subs"]):
        cmd = [
            "yt-dlp", "--skip-download",
            *auto_flag,
            "--sub-langs", SUB_LANGS,
            "--sub-format", "vtt/srt/best",
            "--convert-subs", "vtt",
            "-o", base,
            "--no-warnings",
            url,
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        vtts = list(Path(workdir).glob("sub*.vtt"))
        if vtts:
            text = clean_vtt(vtts[0].read_text(encoding="utf-8", errors="ignore"))
            if text.strip():
                kind = "人工字幕" if auto_flag == ["--write-subs"] else "自動字幕"
                return text, kind
    return None, None


def clean_vtt(raw):
    """把 vtt 字幕清成連續文字：去 header、時間戳、序號、標記、重複行。"""
    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:                      # 時間戳行
            continue
        if re.fullmatch(r"\d+", line):         # 純序號行
            continue
        line = re.sub(r"<[^>]+>", "", line)    # 移除 <c>、<00:00:00.000> 等標記
        line = line.strip()
        if line and (not lines or lines[-1] != line):   # 去掉相鄰重複
            lines.append(line)
    return merge_text(lines)


# ------------------------------------------------------------
#  4. 語音辨識（沒字幕才用）
# ------------------------------------------------------------
def download_audio(url, workdir):
    """下載並抽出音訊，回傳音訊檔路徑。"""
    out = os.path.join(workdir, "audio.%(ext)s")
    cmd = [
        "yt-dlp", "-x", "--audio-format", "mp3",
        "-o", out, "--no-warnings", url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠ 音訊下載失敗：")
        print(result.stderr.strip())
        sys.exit(1)
    mp3s = list(Path(workdir).glob("audio*.mp3"))
    return str(mp3s[0]) if mp3s else None


# ╔══════════════════════════════════════════════════════════╗
# ║  ★ 可抽換模組：語音辨識引擎 ★                              ║
# ║  介面固定：傳入音訊檔路徑，回傳一段純文字字串。           ║
# ║  要改用自己的本地模型時，只需改寫這個函式內部即可，       ║
# ║  其餘流程（下載、清洗、簡轉繁、輸出）完全不用動。         ║
# ╚══════════════════════════════════════════════════════════╝
def transcribe_audio(audio_path):
    """預設使用本地 faster-whisper（CPU、int8）。"""
    from faster_whisper import WhisperModel

    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(audio_path, language="zh", vad_filter=True)
    pieces = [seg.text.strip() for seg in segments if seg.text.strip()]
    return merge_text(pieces)
# ────────────────  可抽換模組結束  ────────────────


# ------------------------------------------------------------
#  5. 清洗文字
# ------------------------------------------------------------
def merge_text(pieces):
    """把多段文字合併成通順段落：以標點作為斷句依據。"""
    joined = "".join(pieces)
    # 在中文句末標點後換行，方便閱讀
    joined = re.sub(r"([。！？!?])", r"\1\n", joined)
    paragraphs = [p.strip() for p in joined.splitlines() if p.strip()]
    return "\n".join(paragraphs)


# ------------------------------------------------------------
#  6. 簡轉繁
# ------------------------------------------------------------
def to_traditional(text):
    from opencc import OpenCC
    cc = OpenCC(OPENCC_CONFIG)
    return cc.convert(text)


# ------------------------------------------------------------
#  7. 輸出
# ------------------------------------------------------------
def write_output(info, text, source_kind):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(info["title"]) + ".txt"
    fpath = OUTPUT_DIR / fname
    header = (
        f"標題：{info['title']}\n"
        f"作者：{info['uploader']}\n"
        f"來源：{info['webpage_url']}\n"
        f"取得方式：{source_kind}\n"
        f"{'-' * 40}\n\n"
    )
    fpath.write_text(header + text, encoding="utf-8")
    return fpath


# ------------------------------------------------------------
#  主流程
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print('用法：python transcribe.py "<影片網址>"')
        sys.exit(1)

    url = sys.argv[1]
    check_environment()

    print("→ 取得影片資訊…")
    info = get_video_info(url)
    print(f"   《{info['title']}》— {info['uploader']}")

    with tempfile.TemporaryDirectory() as workdir:
        print("→ 嘗試抓取現成字幕…")
        text, kind = try_fetch_subtitles(url, workdir)

        if text is None:
            print("   沒有字幕，改用語音辨識…")
            audio = download_audio(url, workdir)
            if KEEP_AUDIO and audio:
                shutil.copy(audio, OUTPUT_DIR / (safe_filename(info["title"]) + ".mp3"))
            text = transcribe_audio(audio)
            kind = f"語音辨識（{WHISPER_MODEL}）"
        else:
            print(f"   抓到{kind}。")

        print("→ 簡轉繁…")
        text = to_traditional(text)

        print("→ 輸出檔案…")
        fpath = write_output(info, text, kind)

    char_count = len(text.replace("\n", ""))
    print()
    print(f"✓ 完成！")
    print(f"   檔案：{fpath}")
    print(f"   方式：{kind}")
    print(f"   字數：約 {char_count} 字")


if __name__ == "__main__":
    main()
