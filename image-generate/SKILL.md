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
- 一律只允許呼叫 `scripts/gemini_generate.py`。
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

## 封面圖（部落格整合）

部落格封面圖**不需要** `gen_cover.py`，直接按照 Step 1 的展開規則把文章標題與 tags 轉成完整 prompt，再呼叫 `gemini_generate.py`。

### 展開方式

給定文章標題 + tags，展開成視覺 prompt 時需要：

- **視覺主題**：從標題擷取核心概念（技術名稱、主題），翻譯成英文描述性視覺畫面
- **畫風**：tech/系統類 → cinematic digital illustration；個人/心得類 → warm editorial illustration；AI 類 → sci-fi, futuristic；資安類 → dark, cyberpunk-adjacent
- **構圖**：封面固定 wide 16:9、dark background with subtle gradient
- **光線**：依畫風推斷（tech → cool blue ambient；personal → warm golden light；security → deep shadows with accent lights）
- **品質詞**：ultra-detailed, sharp focus, high quality, no text, no watermark, no logo

### 範例

```
輸入：
  title: "用 Rust 實作高效能 API Server"
  tags: rust, backend, performance

展開後 prompt：
  "blog post cover image, high-performance Rust server architecture with
   elegant data flow and metallic amber tones, dark cinematic digital
   illustration, wide 16:9 shot with structured geometric layout,
   dramatic side lighting with amber and cool blue contrast, powerful
   and precise mood, dark background with subtle gradient,
   ultra-detailed, sharp focus, high quality render,
   no text, no watermark, no logo"
```

### 呼叫方式

```bash
python3 ~/skills/image-generate/scripts/gemini_generate.py \
  --prompt "<展開後的完整英文 prompt>" \
  --output ~/projects/blog/src/assets/post-covers/<YYYY-MM-DD-slug>.png
```

frontmatter 寫法：
```yaml
coverImage:
  src: "@/assets/post-covers/YYYY-MM-DD-slug.png"
  alt: "文章標題"
```


---

## 初次設定（尚未登入時）

用有頭模式開一個 Chrome 視窗，在裡面登入 Google 帳號，session 會儲存到 profile 目錄：

```bash
playwright-cli open --headed --profile=~/.cache/skills/image-generate/gemini-profile https://gemini.google.com/app
```

登入一次後，後續腳本自動重用同一個 profile，不需要再次登入。

可用 `GEMINI_PROFILE_DIR` 覆蓋預設 profile 目錄。

## 依賴

- `playwright-cli`（`npm install -g playwright-cli`）
- `google-chrome`（`/usr/bin/google-chrome`）
- `python3` 3.10+
- 生成時間約 15–60 秒，timeout 180 秒

## 注意事項

- 腳本**先開 Google 搜尋頁**點擊 Gemini 連結進入，而非直接導航到 `gemini.google.com`。這樣可以帶上正確的 Referer header，避免 Google 回傳 502。
- 使用 **headed（有視窗）模式**，headless Chrome 會被 Google 偵測並 502 封鎖。
- 腳本送出 prompt 後以輪詢方式等待圖片出現，並透過 Voyager URL fetch 下載原始尺寸圖片，失敗時 fallback 到 JS canvas 提取。
- 每次生成完畢後會導航回首頁，確保下次運行狀態乾淨。
