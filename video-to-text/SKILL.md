---
name: video-to-text
description: 把 YouTube 影片網址轉成帶時間戳的繁體中文逐字稿。當使用者貼出影片連結，並想要字幕、逐字稿、影片文案、把影片內容轉成文字、或把影片內容載入對話中討論時，務必使用此 skill。流程為：優先抓取影片現成字幕，抓不到才用本地語音辨識（MOSS + 靜音切片），最後統一簡轉繁體並輸出帶時間戳的文字檔，再把全文帶進對話。
---

# video-to-text

把影片網址轉成一份帶時間戳的繁體中文逐字稿，並把全文帶進對話讓使用者直接討論。

**全本機執行**，不需要任何雲端 API 或付費帳號。

以 **YouTube 為主要目標**；B 站／抖音能跑就跑，不特別保證（yt-dlp 支援即可，但未針對其反爬調校）。

---

## 核心取捨

> **能抓到現成字幕，就絕不浪費算力去做語音辨識。**

這是整個設計的樞紐。實測差距極大：

| 路徑 | 23.5 分鐘影片 | 15.7 分鐘影片 |
| --- | --- | --- |
| 有字幕 | **約 3 秒**，不碰 GPU | — |
| 無字幕（走辨識） | — | **約 7 分鐘**，GPU 全載 |

所以語音辨識是**保底路徑**，不是常態。多數 YouTube 影片有字幕（人工或自動）。

---

## 使用方式

```bash
python /home/benny/skills/video-to-text/transcribe.py "<影片網址>"
```

腳本會自動轉進自己的 venv（見下方「環境」），不需要手動 activate。

完成後：

1. 讀取產出的 `.txt`（預設在 `~/video-transcripts/`）。
2. 把逐字稿全文帶進對話，讓使用者接續討論。
3. 簡短回報：檔案路徑、段數、字數、**取得方式（抓字幕 or 語音辨識）**、耗時。

---

## 流程

```
1. yt-dlp 抓影片資訊（標題／頻道／時長）
2. 路徑 A：抓現成字幕 —— 先人工字幕，再自動字幕，轉成 SRT
   路徑 B：抓不到才下載音訊 → 靜音切片 → MOSS 逐段辨識
3. OpenCC s2twp 轉台灣正體
4. 輸出 .txt（每行一段，開頭一個絕對時間戳）
```

兩條路徑都產生同一種 `Segment(start, end, speaker, text)`，所以時間戳格式一致，
下游只需要一個 formatter。

### 輸出格式

```
# 影片標題
來源：https://www.youtube.com/watch?v=...
頻道：某頻道｜時長：15:39｜取得方式：語音辨識

[00:00] 大家好，我是……
[00:04] 今天我們要來聊聊……
```

---

## 為什麼一定要切片

MOSS-Transcribe-Diarize 是**自迴歸的 audio-LLM**，KV cache 隨長度膨脹，
整段餵進去的耗時是**超線性**的。實測（GTX 1660 SUPER 6GB）：

| 做法 | 939 秒音訊 |
| --- | --- |
| 整段餵進去 | 跑 18 分鐘還沒結束，VRAM 5.8G 逼近爆掉 |
| **切成 60s 段** | **約 7 分鐘**，VRAM 2.6G |

切片長度也實測過，**60 秒是甜蜜點**：

| 片長 | RTF | 外推 939s |
| --- | --- | --- |
| 10s | 0.610 | 9.5 分 |
| 30s | 0.517 | 8.1 分 |
| **60s** | **0.472** | **7.4 分** |
| 120s | 0.522 | 8.2 分 |

### 怎麼切才不會砍斷字

**按靜音切，不按時間切。** 用 `ffmpeg silencedetect` 找出所有靜音區間，
切點只落在靜音的**中點**，字本身永遠在語音區段內部。

若某段連續語音超過 60 秒（有人一口氣講很久），寧可讓該 chunk 長一點也要
等到下一個靜音才切（最多放寬到 2 倍），真的找不到才硬切。

---

## 環境

這個 skill **自給自足**：venv 和模型都在自己的目錄下，刪掉資料夾就全部帶走，
不會在系統各處留下殘留。

```
/home/benny/skills/video-to-text/
├── SKILL.md
├── transcribe.py
├── .venv/          7.1G   torch + CUDA + transformers（.venv/.gitignore 自動排除）
└── models/         1.8G   MOSS 模型（HF_HOME 指向這裡，.gitignore 排除）
```

模型**不放共用的 `~/.cache/huggingface`**。腳本在 import transformers 之前
就把 `HF_HOME` 指到 `models/`，所以下載與載入都走這裡。

依賴裝在 `.venv`，**建在系統 Python 3.14 上**（Ubuntu 26.04 LTS 預設）。
腳本開頭的 `ensure_venv()` 會在被系統 python 呼叫時自動 `os.execv` 轉進去。

| 依賴 | 用途 | 位置 |
| --- | --- | --- |
| yt-dlp | 抓資訊／字幕／音訊 | 全域（`~/.local`） |
| ffmpeg | 抽音訊、靜音偵測、切片 | 系統（apt） |
| torch + CUDA | 跑模型 | `.venv` |
| transformers | 載入 MOSS | `.venv` |
| moss-transcribe-diarize | MOSS 官方推理輔助 | `.venv` |
| opencc | 簡轉繁（`s2twp`） | `.venv`（缺則退回全域 CLI） |

### 重建 venv

```bash
cd /home/benny/skills/video-to-text
python3.14 -m venv .venv                       # 需要 apt 的 python3.14-venv
TMPDIR=~/.cache/pip-tmp .venv/bin/pip install \
    torch torchaudio --index-url https://download.pytorch.org/whl/cu126
TMPDIR=~/.cache/pip-tmp .venv/bin/pip install \
    transformers accelerate numpy soundfile librosa \
    opencc-python-reimplemented \
    "git+https://github.com/OpenMOSS/MOSS-Transcribe-Diarize.git"
```

**`TMPDIR` 一定要設。** 這台 WSL 的 `/tmp` 是 3.9G tmpfs（吃 RAM），
torch + CUDA 套件解壓會直接把它塞爆，錯誤訊息是 `No space left on device`
——即使 `df /home` 顯示還有幾百 GB。腳本內也有 `os.environ.setdefault("TMPDIR", ...)`。

---

## 可調參數

檔案最上方的設定區：

- `OUTPUT_DIR` — 逐字稿存放資料夾（預設 `~/video-transcripts`）
- `CHUNK_SECONDS` — 切片上限（預設 60，實測最佳）
- `SILENCE_DB` / `SILENCE_MIN_S` — 靜音判定門檻（預設 -35dB / 0.35s）
- `OPENCC_CONFIG` — 簡轉繁設定（預設 `s2twp`，含慣用詞轉換）
- `KEEP_AUDIO` — 是否保留下載的音訊（預設 `False`）

---

## 抽換語音辨識引擎

辨識被隔離在單一函式 `transcribe_audio(audio_path, duration) -> [Segment]`，
換引擎只需改寫這個函式，其餘流程完全不動。函式上方有明顯標示。

### 曾評估過的其他引擎

| 引擎 | 結論 |
| --- | --- |
| **faster-whisper** | 原本的預設，在 Python 3.14 上裝不起來（只留下孤兒 `ctranslate2`），已淘汰 |
| **SenseVoice-Small** | 非自迴歸，**同一支影片只要 17.9 秒（52.5x 即時）、VRAM 1.2G**，中文很準。但中英夾雜的技術名詞明顯較弱（`Opus 5 Max` → `op5max`、`Anthropic` → `an`），且不含時間戳需另接 VAD |
| **MOSS-Audio-8B** | 旗艦版，fp16 需約 16GB VRAM，這張 6GB 卡裝不下 |

要換回 SenseVoice：`pip install funasr`，但**它會全域改寫 `huggingface_hub`**，
把後續所有下載導向 ModelScope，會導致 MOSS 從 HF 抓不到模型（404）。
兩者不能在同一個 process 內共存，這也是為什麼靜音偵測改用 ffmpeg 而不是 fsmn-vad。

---

## 已知限制

- **英文／技術名詞會變形**：`Opus 5` 可能被辨識成 `Opt5`、人名可能拼錯。中文本身的辨識品質良好。
- **不輸出講者標籤**：MOSS 支援講者分離，但每個 chunk 是獨立辨識的，跨 chunk 的
  `S01`／`S02` 編號沒有意義（實測獨白影片被標出 158 個 S01 + 3 個 S02）。錯的資料比
  沒有資料更糟，所以直接捨棄。
- **這張卡沒有 Tensor Core**（GTX 16 系列被拿掉了），且 sm_75 無原生 bf16、
  由 torch 軟體模擬。辨識慢的根源在硬體，不是調參能救的。

---

## 故障排除

- **抓不到字幕但影片明明有** → 部分字幕需登入，加 `--cookies-from-browser`。
- **`No space left on device`** → `TMPDIR` 沒設，見上方「重建 venv」。
- **模型下載 404 到 modelscope.cn** → 有東西 import 了 `funasr`，把它移除。
- **CUDA out of memory** → 調小 `CHUNK_SECONDS`（VRAM 隨片長增加：60s→2.6G、120s→3.3G）。
- **某些詞沒轉繁** → OpenCC 詞庫有限，可在輸出後自行做詞彙替換。
