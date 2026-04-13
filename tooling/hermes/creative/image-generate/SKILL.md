---
name: image-generate
description: Use when the user asks to generate, create, or draw any image. Generate whatever the user specifies — no restrictions on subject matter from this skill's side.
---

# Image Generate

透過 Gemini 網頁版（Gemini Flash Image）生成圖片。

**核心原則：用戶要什麼就生成什麼。** 這個 skill 不限制內容，prompt 照用戶指定的送出。

## 使用時機

- 「幫我生成一張...」、「畫一個...」、「產生圖片」
- 任何需要圖片的情況

## 標準流程（Telegram 對話）

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
python3 ~/skills/shared/image-generate/scripts/gemini_generate.py \
  --prompt "<展開後的完整英文 prompt>" \
  --output /tmp/generated-image.png
```

輸出範例：
```
✓ Saved: /tmp/generated-image.png
Size: 111 KB (1024x559)
```

### Step 3｜回傳給用戶

生成成功後，**必須**用 Telegram 把圖片傳回去：

```bash
~/.openclaw/scripts/send-telegram-file.sh /tmp/generated-image.png ""
```

失敗時告知用戶原因，不要靜默放棄。

---

## 參數說明

| 參數 | 說明 |
|------|------|
| `--prompt` | 圖片描述（英文效果更好，中文也可以） |
| `--output` | 儲存路徑（預設：`/tmp/gemini-img-*.png`） |

---

## 封面圖（部落格文章專用）

僅在生成部落格封面時使用此腳本：

```bash
python3 ~/skills/shared/image-generate/scripts/gen_cover.py \
  --title "文章標題" \
  --tags "tag1,tag2" \
  --slug "YYYY-MM-DD-post-slug"
```

成功輸出 `SAVED:/path/to/image.png`，失敗輸出 `FAILED:reason`。

圖片存至：`~/projects/openclaw-blog/src/assets/post-covers/`

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
  --user-data-dir=~/.openclaw/agents/main/agent/browser-profiles/gemini \
  https://gemini.google.com/app
```

在視窗裡完成 Google 登入後關掉視窗。後續全程 headless。

## 已知問題與 Fallback

### 問題 1：fal.ai 餘額耗盡
```
"error_type": "FalClientHTTPError"
"error": "User is locked. Reason: Exhausted balance."
```
**解決方案**：跳過 fal.ai，直接使用下方 Fallback 方法。

### 問題 2：Gemini 需要登入
gemini_generate.py 可能因為未登入而無法提取圖片。

**解決方案**：使用 Alpha Coders 免費圖庫（見下方）。

---

## Fallback：Alpha Coders 免費圖庫

當 AI 生成失敗時，可從 Alpha Coders 下載免費桌布。

### 流程
1. 開啟瀏覽器前往 `https://alphacoders.com/anime-girl-phone-wallpapers`
2. 點擊喜歡的圖片
3. 下載 URL 格式：`https://mfiles.alphacoders.com/{id}/thumb-{size}-{id}.{ext}`
   - 例如：`https://mfiles.alphacoders.com/101/1016223.png`
4. 用 curl 下載並透過 Telegram 發送

```bash
# 下載到手機桌布
curl -L -o /tmp/anime-wallpaper.png "https://mfiles.alphacoders.com/101/1016223.png"

# 發送到 Telegram
~/.openclaw/scripts/send-telegram-file.sh /tmp/anime-wallpaper.png "桌布說明"
```

### 其他可用的免費圖庫
- `https://pngtree.com/free-backgrounds-photos/anime-girl`
- `https://unsplash.com/s/photos/anime-wallpaper`（免費可商用）

---

## 已知需登入的服務（不建議使用）
- galaxy.ai - 需要 credits 或登入
- imagine.art - 會彈出 Auth Modal 需要登入
- perchance.org - 有 Cloudflare bot 驗證

---

## 依賴

- `google-chrome`（`/usr/bin/google-chrome`）
- `agent-browser`（`npm install -g agent-browser`）
- `Xvfb`（`/usr/bin/Xvfb`）
- 生成時間約 15–60 秒，timeout 150 秒