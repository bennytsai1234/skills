---
name: rss-morning-report
description: 每天台北時間 08:00 執行。從本地 RSS 彙整檔挑 3–5 個當天最重要的 AI 主題，寫成有深度觀點的「AI 晨間精選」。繼承 _blog-publisher-base。
---

# rss-morning-report（AI 晨間精選）

**發文時段**：每天 `08:00`（台北）
**系列**：`daily-ai-report`
**定位**：精選、有深度、有觀點。從上百條 RSS 挑 3–5 個最值得花時間的主題，每個主題寫出分析段落。

此 skill 的風格規則、frontmatter schema、L1–L4 自檢、發佈管線全部繼承自
`~/skills/_blog-publisher-base/SKILL.md`。下面只寫這個 variant 獨有的步驟。

---

## Variant 變數

```
SLOT_ID       = ai-news-morning
PUBLISH_HHMM  = 08:00
COVER_TITLE   = AI 晨間精選｜YYYY-MM-DD
COVER_TAGS    = AI,morning,daily
COMMIT_PREFIX = docs: AI 晨間精選
SERIES        = daily-ai-report
```

---

## Step 1｜讀取今日 RSS 資料

```bash
cat ~/ai-intel/hourly/$(date +%Y-%m-%d).json
```

檔案由 OS/openclaw cron 多次抓取後追加去重寫入。若當天檔案不存在或為空陣列：

```bash
bash ~/ai-intel/scripts/fetch-rss.sh
```

再讀一次。仍為空 → 走 base 的「唯一允許跳過」分支：`exit 1`。

---

## Step 2｜挑 3–5 個主題

篩選標準：

- 產業影響力大：大公司戰略、重大融資、產品上下線
- 技術突破性高：新模型、重要研究成果、開源釋出
- 與 OpenClaw / Anthropic / OpenAI / Google / Meta / NVIDIA 生態相關
- 開發者社群熱度高（GitHub Trending、社群熱議）

排除：

- 普通 arXiv 論文（除非特別有影響力）
- 一般產品更新、版本號升級
- 與 AI 無直接關聯的泛科技新聞

同一事件有多條來源時合併寫一個主題。

---

## Step 3｜深度搜尋（可選）

RSS 摘要不夠時用 `web_search` / `web_fetch` 補：

- 原始報導全文
- 官方公告、部落格
- 數據佐證（融資金額、用戶數、benchmark）

---

## Step 4｜寫作

套用 base 的風格規則。文章結構如下：

```markdown
## 今日觀察

一段 3–5 句的總結性開場，用粗體標出核心觀點，把今天幾個主題的共同脈絡或產業趨勢串起來。
（記得不要寫「隨著 AI 的快速發展」這類空話開頭，要從具體事件切入。）

---

## 主題一標題 — 副標題（點出為什麼重要）

2–4 段深度段落。事實 → 數據 → 產業影響分析，段落間有邏輯推進。

---

## 主題二標題 — 副標題

同上風格。

---

## 主題三標題 — 副標題

同上風格。（最少 3 個主題，最多 5 個）

---

## 其他值得關注

- **主題名稱**：一句話摘要，點出為什麼值得注意。
- **主題名稱**：一句話摘要。
- **主題名稱**：一句話摘要。

---

## 參考連結

- [報導標題](URL)
- [報導標題](URL)
```

### Frontmatter

```yaml
---
title: "AI 晨間精選｜YYYY 年 M 月 D 日"
description: "用一句話概述今天 2–3 個最大的事"
publishDate: "YYYY-MM-DDT08:00:00+08:00"
updatedDate: "YYYY-MM-DDTHH:MM:00+08:00"   # 執行當下時間
tags: ["具體公司", "具體產品", "具體主題"]
series: "daily-ai-report"
seriesOrder: N
draft: false
---
```

`seriesOrder` 計算：

```bash
ls ~/projects/openclaw-blog/src/content/post/ \
  | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}-ai-news-' | wc -l
```

取結果 +1（除非今天已經寫過一篇，則沿用同一個 seriesOrder）。

---

## Step 5｜交給 base 的 Pipeline

依序執行 `_blog-publisher-base/SKILL.md` 的 Pipeline Step A → F，使用本文件上方的 Variant 變數。執行完畢輸出摘要：

```
rss-morning-report 完成

日期：YYYY-MM-DD
slot：08:00 (YYYY-MM-DDT08:00:00+08:00)
精選主題：N 個
其他關注：N 則
檔案：YYYY-MM-DD-ai-news-morning.md
封面：已生成 / 跳過
自檢：L1 ✅ / L2 ✅ / L3 ✅ / L4 ✅
build：通過
push：成功
```

---

## Light Issue 處理

RSS 條目品質太低或主題數 < 3 時，走 base 的 Light Issue 模式：

- 降標收 2–3 個相對最好的主題
- 正文寫完整，不砍結構
- commit 訊息加 `[light-issue]` 後綴
- 依然 push，不 `exit 1`

只有當 RSS 檔案完全為空且 `fetch-rss.sh` 也拉不回內容時，才允許 `exit 1`。
