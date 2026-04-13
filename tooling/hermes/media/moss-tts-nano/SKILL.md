---
name: moss-tts-nano
description: MOSS-TTS-Nano — 0.1B parameter multilingual TTS model. CPU-friendly, auto-downloads from HuggingFace on first run, voice cloning support. Apache 2.0 license. Use for lightweight local text-to-speech generation.
version: 1.0.0
author: Mamba Team
dependencies: [transformers, torch, torchaudio, fastapi, uvicorn, sentencepiece, WeTextProcessing, soundfile]
metadata:
  hermes:
    tags: [TTS, Text-to-Speech, Voice Cloning, MOSS, CPU, Multilingual, Audio]

---

# MOSS-TTS-Nano — Lightweight Local TTS

0.1B 參數多語言語音合成模型，純 CPU 運行，4 核心即可即時生成。

## 適合場景

- 本地語音合成（不需要 API）
- 語音克隆（提供參考音頻）
- 低資源環境（無 GPU）
- 說明：如果你有 15+ GB RAM 也可以考慮 MOSS-TTS-Local-Transformer（3B）

## 關鍵特性

| 特性 | 數值 |
|------|------|
| 參數量 | 0.1B |
| 輸出格式 | 48 kHz, 16-bit, 雙聲道 WAV |
| 延遲 | 即時（4 核心 CPU） |
| 語言 | 20 種（含中文） |
| 授權 | Apache 2.0 |

## 安裝步驟

```bash
# 1. Clone
git clone https://github.com/OpenMOSS/MOSS-TTS-Nano.git ~/projects/MOSS-TTS-Nano

# 2. 建立虛擬環境（用 uv + Python 3.12，conda 非必要）
cd ~/projects/MOSS-TTS-Nano
uv venv .venv --python /usr/bin/python3.12

# 3. 安裝依賴
uv pip install --python .venv -r requirements.txt

# 4. 安裝本體
uv pip install --python .venv -e .
```

## 使用方式

### 語音克隆（推薦）
```bash
cd ~/projects/MOSS-TTS-Nano
source .venv/bin/activate

python infer.py \
  --prompt-audio-path assets/audio/zh_1.wav \
  --text "你好，這是測試語音。" \
  --device cpu \
  --output-audio-path generated_audio/output.wav
```

內建參考音頻：`assets/audio/zh_*.wav`（中文）、`assets/audio/en_*.wav`（英文）、`assets/audio/jp_*.wav`（日文）

### 純 TTS（無克隆）
```bash
python infer.py \
  --text "Hello world" \
  --mode continuation \
  --device cpu
```

### Web 介面
```bash
python app.py
# 瀏覽器打開 http://127.0.0.1:18083
```

### CLI 指令
```bash
moss-tts-nano generate --text "文字" --prompt-audio-path ref.wav
moss-tts-nano serve
```

## Telegram 語音訊息轉換

MOSS-TTS 輸出 WAV，但 Telegram 語音訊息需要 OGG（Opus）格式：

```bash
ffmpeg -i output.wav -c:a libopus -b:a 32k output.ogg -y
```

## 常見問題

### Q: 出現「Access denied」錯誤？
A: 確認是 `OpenMOSS-Team/MOSS-TTS-Nano`（Apache 2.0，**不需要**登入或 token）。如果是 `MOSS-TTS-GGUF` 或 `MOSS-Audio-Tokenizer-ONNX`，那些是 gated，需要另外申請授權。

### Q: 推斷時記憶體不足？
A: 模型會自動下載到 `~/.cache/huggingface/`。可用 `HF_HUB_OFFLINE=1` 強制使用本地快取。

### Q: 沒有 GPU，會用 CPU 嗎？
A: 加上 `--device cpu`，代碼會自動偵測並使用 CPU。

### Q: WeTextProcessing 安裝失敗？
```bash
pip install git+https://github.com/WhizZest/WeTextProcessing.git
```

## 與 Whisper 的組合

MOSS-TTS-Nano 是 TTS（文字→語音）， Whisper 是 STT（語音→文字）。兩者組合可以做：
- 語音轉文字（Whisper）→ 修改內容 → 語音合成（MOSS-TTS-Nano）
- 音色克隆：參考音頻（Whisper 轉寫）→ 用同樣音色說新內容

## 資源

- GitHub: https://github.com/OpenMOSS/MOSS-TTS-Nano
- HuggingFace: https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano
- License: Apache 2.0
