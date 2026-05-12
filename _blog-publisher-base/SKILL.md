---
name: _blog-publisher-base
description: 不直接呼叫。給 rss-morning-report / daily-tech-digest / daily-ai-report / article-to-blog 繼承，定義 openclaw-blog 的 frontmatter schema、寫作風格規則、L1–L4 自檢流程與發佈管線。
---

# _blog-publisher-base

所有 openclaw-blog 的自動寫稿 skill 共用的底座。**不要單獨觸發這個 skill**，它只是給 variant 繼承用的。

## 使用方法

每個 variant 的 SKILL.md 都會先列出自己獨有的「取材 / 篩選 / 寫作焦點」步驟，然後在最後階段宣告：

```
接下來依序套用 ~/skills/_blog-publisher-base/SKILL.md 的 Pipeline 章節（從「Pipeline Step A」到「Pipeline Step F」），並使用下列 variant 變數：

- SLOT_ID        = <variant 專屬，例如 ai-news-morning>
- PUBLISH_HHMM   = <HH:MM，例如 08:00>
- COVER_TITLE    = <封面標題>
- COVER_TAGS     = <封面 tag 清單>
- COMMIT_PREFIX  = <commit 訊息前綴>
- SERIES         = <frontmatter series 值，可留空>
```

Variant 若有需要（例如 article-to-blog 的 slug 是動態的），可覆寫某一個 Pipeline Step 的對應欄位，其餘照套。

---

## 1. Frontmatter schema（權威定義）

`openclaw-blog` 的 `src/content.config.ts` 目前定義如下（2026-04 更新）：

```ts
// post collection
{
  title: z.string().max(60),                       // 必填
  description: z.string(),                          // 必填，一句話
  publishDate: z.string().or(z.date()),             // 必填，ISO 8601 首選
  updatedDate: z.string().optional(),               // 選填
  tags: z.array(z.string()).default([]),            // 選填
  draft: z.boolean().default(false),                // 選填
  pinned: z.boolean().default(false),               // 選填
  coverImage: { alt: string, src: image }.optional(),
  ogImage: z.string().optional(),
  series: z.string().optional(),
  seriesOrder: z.number().int().positive().optional(),
}
```

**⚠️ 2026-04-12 修正之前的版本沒有 `series` / `seriesOrder`，舊文章雖然寫了也會被 schema 靜默丟掉。現在是正式欄位，要照用。**

### 必填欄位與格式

```yaml
---
title: "【分類前綴】具體標題，不超過 60 字"
description: "一句話，20–40 字，說清楚這篇文章在講什麼"
publishDate: "YYYY-MM-DDTHH:MM:00+08:00"
updatedDate: "YYYY-MM-DDTHH:MM:00+08:00"
tags: ["具體公司", "具體技術", "不能是 AI 這種空標籤"]
draft: false
---
```

### publishDate 規則

- **一律使用 ISO 8601 含時區** `YYYY-MM-DDTHH:MM:00+08:00`，不要用純日期字串。
- `HH:MM` 取 variant 的 `PUBLISH_HHMM`（例如晨間精選是 `08:00`），不是執行當下時間。這樣部落格按時間排序時不會被「同一天誰先誰後」搞亂。
- 就算同一天重跑，publishDate 保持不變；覆寫只更新 updatedDate。

### updatedDate 規則

- 每次寫入/重寫檔案時，**更新為執行當下的時間**，精度到分鐘：
  ```bash
  date +%Y-%m-%dT%H:%M:00+08:00
  ```
- 第一次寫入時，updatedDate 可以等於 publishDate（都是當天的 slot 時間）也可以填實際執行時間，選後者比較誠實。
- 如果 variant 有「對同一天既有檔案做修補」的情境（例如 Light Issue 模式重寫），updatedDate 一定要換成當下時間。

### series / seriesOrder

- `series` 填該 variant 所屬的系列 slug（若有，例如 `daily-ai-report`），與 `src/content/series/<slug>.md` 對齊。
- `seriesOrder`：寫入前數當天之前的同系列檔案 + 1，或根據 variant 自行指定。
- 非系列文章（例如 article-to-blog 的技術解析）兩個欄位都留空。

### tags 規則

- 至少 2 個、最多 6 個。
- 只寫「具體的公司 / 產品 / 技術名詞」，不寫 `AI`、`LLM`、`morning report` 這種空標籤。
- 好例：`["OpenAI", "GPT-5", "reasoning"]`；壞例：`["AI", "新聞", "科技"]`。

### 篇幅與密度規則（新增）

所有 blog 類文章預設都要比過去更耐讀，不准再用「短而薄」的摘要混過去。

- **短文下限**：900 字。除非走 Light Issue，否則不得低於此數。
- **標準技術解析**：1200–1800 字。
- **深度研究 / 專題解析**：1800–2600 字。
- **每個主題段** 至少回答三件事：
  1. 它到底做了什麼
  2. 它跟既有做法差在哪裡
  3. 為什麼工程師現在要在意
- **每篇至少要有 3 個具體錨點**：數字、產品名、模型名、論文名、公司名、程式庫名，不能只有抽象概念。
- **每 250–400 字要有一個新的信息增量**，不能只是重講上一段。
- **觀點段不可缺席**：至少要有一段清楚講作者判斷，而不是只把資料重排。

### 研究強化規則（新增）

所有 blog 類 skill 在動筆前都要先補足研究，不准只靠單一摘要來源。

最低要求：

1. **原始來源至少 1 個**
   - 官方公告、原論文、原始 repo、原始技術文其中之一。
2. **側面來源至少 2 個**
   - 媒體報導、開發者文章、文件頁面、benchmark 頁面、GitHub README 都可以。
3. **交叉比對至少 1 次**
   - 對一個關鍵事實（例如分數、價格、時間、限制）做跨來源確認。
4. **資料不夠時先補搜，不要硬寫**
   - 如果只有一份摘要，先 `web_search` / `web_fetch` 補官方來源與背景資料。

### 段落品質規則

所有段落都要有內在推進重心，不是同義改寫或資訊轉述。每段至少具備以下一項：

- **往前揭開了什麼**：引入一個之前沒提過的技術事實、反直覺現象、或卡點
- **解釋了為什麼**：讓讀者理解一個方法的由來或限制，不再只是描述表面
- **給出了判斷**：作者立場明確，不是純中立陳述

若是技術故事型寫法，小節的承接感比嚴格元素覆蓋更重要——只要段落間有自然的敘事推進，即使某段以描述為主也可以接受。

---

## 2. 寫作風格（所有 variant 共用）

定位：**繁體中文技術部落格**。目標讀者是有基礎技術背景的工程師，不是一般科技新聞讀者。風格偏「冷靜的同行在跟你聊剛讀完的論文／發表」，不是「AI 摘要機」。

### 硬性原則

1. **具體開頭**：第一句從一個**具體的、當下的事件**切入，例如「OpenAI 今天凌晨公開了 GPT-5 的 system card」。禁止「在當今 AI 快速發展的時代」、「隨著技術的不斷進步」、「我們都知道」這類空話開頭。
2. **具體工具／產品名**：一律寫 `Claude Code`、`Gemini 2.5 Pro`、`Llama 4 Scout`、`DeepSeek V4`，不寫「AI 工具」、「某個模型」、「主流大廠」、「相關技術」。
3. **用自己的話重寫**：不抄貼原文，不翻譯，要把事實整理過、排序過再寫出來。
4. **有觀點**：每個主題都要回答「這件事為什麼重要 / 對誰有用 / 改變了什麼」，不是純中立摘要。
5. **數據支撐**：有融資金額、benchmark、參數數量、token 價格這類具體數字時必寫。
6. **Body 從 `##` 開始**：**禁止**在 body 開頭寫 `# 標題`（H1），主題會自動把 frontmatter `title` 渲染成 H1。
7. **文末必有 `## 參考連結`**：列出所有引用過的 URL（官方公告、論文、原始報導）。

### 禁用詞（L1 掃描用）

以下是 AI 生成內容的高頻踩雷詞，**一出現就必須替換或刪除**：

| 禁用 | 替換建議 |
|------|----------|
| 說白了 | 坦白說 / 其實就是 |
| 本質上 | 說到底 / 其實 |
| 綜上所述 / 總的來說 | 刪除，改用具體回扣句 |
| 不可否認 | 直接刪除，改正面陳述 |
| 值得注意的是 / 不難發現 | 直接刪除，改直述 |
| 意味著什麼 / 這意味著 | 所以會發生什麼 / 結果是 |
| 換句話說 | 也就是說 / 你想想看 |
| 首先…其次…最後 | 用自然轉場詞，或改成散文敘述 |
| 讓我們來看看 / 接下來讓我們 | 直接進入下一段 |
| 在當今 XX 的時代 / 隨著 XX 的發展 | 刪除，改具體事件切入 |

### 結構套話

- 連續 4 個以上 bullet point 羅列觀點 → 改成散文敘述
- 大段加粗（超過 2 行的 `**...**`）→ 改成普通文字
- 每段開頭都用「首先」「其次」「此外」「最後」→ 改自然轉場

---

## 3. L1–L4 四層自檢

寫完後必須跑完四層，任何一層失敗就回去改，不是「大致 OK 就 push」。

### L1｜硬性規則掃描（機械層）

| 檢查 | 通過標準 |
|------|----------|
| L1-1 禁用詞 | 上表所有禁用詞零命中 |
| L1-2 結構套話 | 「讓我們看看」「在當今」「隨著發展」零命中；bullet point 連續 ≤4 個；無大段加粗 |
| L1-3 工具名具體性 | 無「AI 工具」「某個模型」「主流大廠」「相關技術」之類空泛詞 |
| L1-4 Body 結構 | Body 開頭是 `##` 而非 `#` |
| L1-5 Frontmatter | `publishDate` / `updatedDate` 皆為 ISO 8601 `+08:00`；`tags` 至少 2 個且具體 |
| L1-6 參考連結 | 文末有 `## 參考連結` 且至少 1 條 URL |

### L2｜風格一致性（模式層）

| 檢查 | 通過標準 |
|------|----------|
| L2-1 開頭 | 第一句是具體事件 / 現象 / 時間 / 產品切入，不是宏大敘事 |
| L2-2 段落節奏 | 段落間有承接推進，不是接龍式陳述同一件事 |
| L2-3 有立場 | 至少在中段或後段有明確作者判斷，不是全篇純中立摘要 |
| L2-4 繁中純度 | 無簡體字、無中國大陸特有詞彙（視頻／軟件／硬盤／運營…），替換為繁中常用（影片／軟體／硬碟／營運） |

### L3｜內容質量（深度層）

| 檢查 | 通過標準 |
|------|----------|
| L3-1 觀點支撐 | 每個核心觀點都有具體數字、產品名、公司名或論文名支撐 |
| L3-2 用自己的話 | 隨機抽兩段與原始來源比對，句式／用詞有明顯差異 |
| L3-3 事實正確 | 公司名、產品名、數字、日期皆正確；不確定的資訊改用「據 X 報導」而非斷言 |
| L3-4 可讀性 | 非該領域專家的工程師也能讀懂，但不為了白話犧牲技術準確度 |
| L3-5 研究完整度 | 至少 1 個原始來源 + 2 個側面來源；關鍵事實有交叉比對 |
| L3-6 信息密度 | 技術故事型：讀完後有那種「我好像懂得比讀之前多了一點」的感覺，不是只多了幾個形容詞 |
| L3-7 敘事推進 | 段落之間有時間順序或因果順序，不是並排幾個獨立觀察湊在一起 |

### L4｜終審（整體層）

通讀全文一次，回答這個核心問題：

> **「我把這段貼給一個不看 AI 新聞的工程師朋友，他讀完後會不會覺得：『這篇好像有點意思，不是那種看完就忘的摘要』？」**

技術故事型寫法還要額外檢查這件事：

- 文章有沒有那種「讓人想繼續讀下去」的拉力，還是一開始就把全部結論交代完了
- 整篇看下來，有沒有哪一段感覺像是硬湊的、跟前後段沒有承接的
- 讀完後，會不會讓人想回去再翻原文

若答案是「感覺像是一開始就講完了、讀到最後沒有力氣了」，找出對應段落重寫。


### 自檢輸出（寫在執行日誌，非文章內容）

⚠️ **重要**：自檢報告是給 cron delivery 的內部執行摘要用的，**千萬不要**寫進 Markdown body。

variant 在 Pipeline Step D 結束後，只把自檢結果輸出到 STDOUT（這樣會進入 cron log），不要 append 到 POST_PATH 檔案裡。

```
## 自檢報告
L1 硬性規則: ✅/❌（命中項: ...）
L2 風格:     ✅/❌（命中項: ...）
L3 內容:     ✅/❌（命中項: ...）
L3-7 敘事推進: ✅/❌
L4 終審:     ✅/❌（問題段落: ...）
總評: PASS / NEEDS-FIX
```

---

## 4. Pipeline（所有 variant 通用的發佈管線）

Variant 在完成自己的「取材 + 寫作」後，照這個順序執行以下六個 Step。

### Pipeline Step A｜決定檔名與路徑

```bash
BLOG_DIR=~/projects/openclaw-blog
TODAY=$(date +%Y-%m-%d)
SLUG="${TODAY}-${SLOT_ID}"          # variant 若需要自訂 slug（article-to-blog）可覆寫
POST_PATH="${BLOG_DIR}/src/content/post/${SLUG}.md"
```

若同日同 slug 檔案已存在 → 直接覆寫（updatedDate 要換成當下時間）。特殊情況（例如 daily-ai-report 想保留歷史版本）再用 `${SLUG}-v2.md` 遞增。

### Pipeline Step B｜決定時間戳

```bash
PUBLISH_DATE="${TODAY}T${PUBLISH_HHMM}:00+08:00"
UPDATED_DATE=$(date +%Y-%m-%dT%H:%M:00+08:00)
```

`PUBLISH_HHMM` 是 variant 提供的固定 slot 時間（08:00 / 10:00 / 12:00 / 15:00）。`UPDATED_DATE` 是執行當下實際時間。

### Pipeline Step C｜生成封面圖

**腳本路徑**：`~/skills/image-generate/scripts/gemini_generate.py`

**Step 1 — 展開 prompt**：根據 `$COVER_TITLE`（文章標題）+ `$COVER_TAGS`（tags），展開成完整英文視覺 prompt。展開規則：

- 從標題提取核心視覺概念，翻譯成英文描述性畫面
- 推斷畫風：tech/系統 → `cinematic digital illustration`；AI → `sci-fi futuristic`；資安 → `dark cyberpunk-adjacent`；個人/心得 → `warm editorial illustration`
- 構圖固定：`blog post cover image, wide 16:9`
- 光線依畫風推斷：tech → `cool blue ambient`；personal → `warm golden light`；security → `deep shadows with red and blue accent lights`
- 品質詞固定：`dark background with subtle gradient, ultra-detailed, sharp focus, high quality, no text, no watermark, no logo`

**Step 2 — 呼叫腳本**：

```bash
python3 ~/skills/image-generate/scripts/gemini_generate.py \
  --prompt "<展開後的完整英文 prompt>" \
  --output ~/projects/openclaw-blog/src/assets/post-covers/$SLUG.png
```

- 成功（exit 0 且檔案存在）→ frontmatter 加入：
  ```yaml
  coverImage:
    src: "@/assets/post-covers/<SLUG>.png"
    alt: "<封面 alt，通常等於 COVER_TITLE>"
  ```
- 失敗 → 跳過封面圖，文章照常發布，不視為任務失敗。

### Pipeline Step D｜寫入 Markdown 檔案

把 variant 寫好的 body 套進 frontmatter，寫入 `$POST_PATH`。**新建檔案或整篇重寫時，一律直接用 `write` 覆寫完整內容，不要對整篇文章做 `edit`。** 只有在「已經 read 過最新檔案內容，且只改很小一段」的情況下，才使用 `edit`。

若同日同 slug 檔案已存在：
- 需要整篇重寫或大幅改寫 → 直接 `write` 覆寫完整檔案
- 只修一小段文字 / frontmatter 單欄位 → 先 `read`，確認最新內容後再 `edit`

寫入後跑一次完整的 L1–L4 自檢。

寫入前最後再檢查一次：

- 字數是否達到 variant 要求
- 是否真的引用了原始來源與側面來源
- 是否至少有一段「我的觀點 / 我的判斷」
- 是否避免了只把素材重新排版的假深度

### Pipeline Step E｜Astro build 驗證

```bash
cd "$BLOG_DIR"
npm run build
```

必須通過（exit 0）。若失敗 → 依據錯誤訊息修正 frontmatter 或 body，再跑一次；**不可** `git push` 一個 build 失敗的 commit。

### Pipeline Step F｜Git commit & push

```bash
cd "$BLOG_DIR"
git add "src/content/post/${SLUG}.md" src/assets/post-covers/
git commit -m "${COMMIT_PREFIX} ${TODAY}"
git push || { echo "[ERROR] Git push failed! Check credentials and network."; exit 1; }
```

Light Issue 模式時 commit 訊息加 `[light-issue]` 後綴：
```
${COMMIT_PREFIX} ${TODAY} [light-issue]
```

---

## 5. Light Issue 模式

當素材稀薄（RSS 條目 < 5、橘鴉 issue 少於 3 條、可選題目只剩 1 篇且品質勉強），**不能靜默跳過**，要走 Light Issue：

- 降低篩選標準，用當天相對最好的素材寫短版（字數砍半也可以）。
- Frontmatter 照常，commit 訊息加 `[light-issue]` 後綴。
- 一樣 `git push`，不 `exit 1`。

**唯一允許直接跳過的情況**：素材完全為 0（RSS 檔案不存在或為空陣列，且即時抓取也拿不到）。這種情況必須 `exit 1` 觸發 cron failureAlert。

---

## 6. 執行摘要輸出格式

所有 variant 執行完畢時，輸出下列格式給 cron log：

```
<variant 名稱> 完成

日期：YYYY-MM-DD
slot：HH:MM (PUBLISH_DATE)
檔案：<SLUG>.md
封面：已生成 / 跳過
自檢：L1 ✅ / L2 ✅ / L3 ✅ / L4 ✅
build：通過
push：成功
```

Light Issue 時在「狀態」那行補一句：`模式：Light Issue（原因：…）`。

---

## 7. 常見坑

- **publishDate 寫成純日期** → 部落格按時間排序時變成 00:00，導致同一天多篇的順序不可預期。一定要含 HH:MM。
- **字數看起來有到，其實內容是空的** → 增加字數不等於增加價值。要增加的是研究面向、比較、案例、觀點，不是同義改寫。
- **只靠單一摘要來源** → 很容易把錯誤資訊直接擴散。至少補一個官方來源和一個側面來源。
- **updatedDate 留成寫稿前一天** → 訂閱端會認為文章沒更新。每次寫入都要 refresh。
- **tags 塞進 `"AI"`、`"LLM"`、`"morning report"`** → 部落格的 tag 頁被這些空標籤灌爆。只填具體對象。
- **直接 `git add -A`** → 會把 digest-selection-log、封面暫存檔都 commit 進 blog repo。只 add 指定檔案與 post-covers。
- **把研究素材（web_fetch / web_search dump）寫在 `src/content/post/` 下** → 雖然 Astro 的 post glob 只吃 `.md/.mdx` 不會建錯，但會污染 repo。研究暫存檔一律放 `~/ai-intel/research-artifacts/<date>-<slug>-research.json`；blog repo 已經 gitignore 掉 `src/content/post/*-research.json`，不要刻意繞過。
- **剛寫完全文又立刻用 `edit` 大範圍補改** → 很容易因為 `oldText` 不再精準命中而整個 cron 判定失敗。整篇覆寫請直接 `write`；小修才用 `edit`，而且一定先 `read` 最新內容。
- **Body 開頭寫 `# 標題`** → 前端會渲染出兩個 H1。
- **用 `npm run check`** → 有些 variant 以前是這樣寫，現在統一用 `npm run build`，後者會同時驗 schema + build 產物，更可靠。
