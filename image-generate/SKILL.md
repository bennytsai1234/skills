---
name: image-generate
description: Use when the user asks to generate, create, or draw any image. Generate whatever the user specifies — no restrictions on subject matter from this skill's side.
---

# Image Generate

透過 Gemini 網頁版（Gemini Flash Image）生成圖片。

**核心原則：用戶要什麼就生成什麼。** 這個 skill 不限制內容，prompt 照用戶指定的送出。

## 強限制

- 不要使用 `browser_*` 工具手動操作 Gemini 網頁。
- 不要自己 `browser_navigate`、`browser_click`、`browser_type` 去拼湊流程。
- 一律只允許呼叫 `scripts/gemini_generate.py` 或 `scripts/gen_cover.py`。
- 如果腳本失敗，直接回報錯誤並停止；不要 fallback 成手動點網頁。

## 使用時機

- 「幫我生成一張...」、「畫一個...」、「產生圖片」
- 任何需要圖片的情況

## 標準流程

### Step 1｜展開提示詞

用戶通常只給簡短描述。**在生成前，先把它展開成完整的英文 prompt。**

展開規則：
- 翻譯成英文
- 補充畫風（photorealistic / illustration / cinematic / anime 等，依描述推斷）
- 補充構圖（full body / close-up / wide shot 等）
- 補充光線與氛圍（natural light / golden hour / studio lighting 等）
- 補充品質詞（high quality, detailed, 8K, sharp focus 等）
- 保留用戶的核心意圖，不做內容替換

範例：
```
用戶輸入：「賽博龐克城市夜景」

展開後：
"A futuristic cyberpunk cityscape at night, neon lights reflecting
on wet streets, towering skyscrapers with holographic advertisements,
dense fog, cinematic composition, photorealistic, ultra detailed, 8K"
```

展開後的 prompt 不需要先問用戶確認，直接進 Step 2。

---

### Step 2｜生成圖片

```bash
python3 ~/skills/image-generate/scripts/gemini_generate.py \
  --prompt "<展開後的完整英文 prompt>" \
  --output /tmp/generated-image.png
```

輸出範例：
```
✓ Saved: /tmp/generated-image.png
Size: 111 KB (1024x559)
```

### Step 3｜回傳結果

生成成功後，至少要回覆圖片檔案路徑與結果。

如果當前執行環境有自己的檔案回傳腳本，可額外傳回去：

```bash
$SEND_FILE_CMD /tmp/generated-image.png
```

若沒有這類整合，直接回報輸出檔案路徑即可。

失敗時告知用戶原因，不要靜默放棄。

---

## 參數說明

| 參數 | 說明 |
|------|------|
| `--prompt` | 圖片描述（英文效果更好，中文也可以） |
| `--output` | 儲存路徑（預設：`/tmp/gemini-img-*.png`） |

---

## 封面圖（選用：部落格整合）

僅在生成部落格封面時使用此腳本：

```bash
python3 ~/skills/image-generate/scripts/gen_cover.py \
  --title "文章標題" \
  --tags "tag1,tag2" \
  --slug "YYYY-MM-DD-post-slug"
```

成功輸出 `SAVED:/path/to/image.png`，失敗輸出 `FAILED:reason`。

若未提供 `--output`，圖片預設存至 `BLOG_ASSETS_DIR`，預設值為：`~/projects/blog/src/assets/post-covers/`

frontmatter 寫法：
```yaml
coverImage:
  src: "@/assets/post-covers/YYYY-MM-DD-slug.png"
  alt: "文章標題"
```

---

## 初次設定（profile 尚未登入時）

```bash
google-chrome --remote-debugging-port=9222 --no-first-run \
  --user-data-dir=~/.cache/skills/image-generate/gemini-profile \
  https://gemini.google.com/app
```

可用 `GEMINI_PROFILE_DIR` 覆蓋預設 profile 目錄。登入一次後，後續可 headless 重用。

## 依賴

- `google-chrome`（`/usr/bin/google-chrome`）
- `agent-browser`（`npm install -g agent-browser`）
- `Xvfb`（`/usr/bin/Xvfb`）
- 生成時間約 15–60 秒，timeout 180 秒

## 注意事項

- 腳本直接在 Gemini 聊天輸入框打字（前綴 `Generate an image:`），不點「建立圖像」按鈕，以避免 style picker 干擾。
- 生成完畢後不會刪除對話，僅導航回首頁確保下次運行乾淨。
- 啟動時會自動清理 WSL 環境中的孤兒 Xvfb/Chrome 進程和過期 lock 檔。
