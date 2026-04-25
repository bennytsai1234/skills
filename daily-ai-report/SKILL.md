---
name: daily-ai-report
description: 每天台北時間 12:00 執行。從橘鴉 Juya 的 juya-ai-daily GitHub Pages 取當天完整 issue 內容，過濾三層關鍵字後由 AI 消化寫成部落格文章。繼承 _blog-publisher-base。
---

# daily-ai-report

**發文時段**：每天 `12:00`（台北）
**系列**：`daily-ai-report`
**資料來源**：[橘鴉 Juya AI 早報 GitHub Pages](https://imjuya.github.io/juya-ai-daily/)（比 B 站說明欄更完整，每條新聞都有摘要 + 原始連結）

風格規則、schema、L1–L4 自檢、發佈管線全部繼承 `_blog-publisher-base/SKILL.md`。

---

## Variant 變數

```
SLOT_ID       = ai-news-daily
PUBLISH_HHMM  = 12:00
COVER_TITLE   = AI 新聞精選｜YYYY-MM-DD
COVER_TAGS    = AI,news,daily
COMMIT_PREFIX = docs: AI 新聞
SERIES        = daily-ai-report
```

---

## Step 1｜確認今天有新 issue

```
web_fetch("https://imjuya.github.io/juya-ai-daily/")
```

首頁索引格式：

```markdown
## [2026-04-12](https://imjuya.github.io/juya-ai-daily/issue-57/)
## [2026-04-11](https://imjuya.github.io/juya-ai-daily/issue-56/)
```

- 有今天 → Step 2
- 沒有今天 → `exit 1`（讓 cron failureAlert 知道，不要靜默）

---

## Step 2｜抓當天完整內容

```
web_fetch("https://imjuya.github.io/juya-ai-daily/issue-{N}/")
```

內容格式：

```markdown
## 概览

### 要闻
- 谷歌推出 Lyria 3 Pro 音乐模型... [↗](#1) #1

### 开发生态
- Google 明确 Gemini CLI 使用权限... #4

### 产品应用
- OpenClaw 发布新版... #10
- MiniMax 开源 Office Skills... #12
```

每條新聞都有 `#數字` 編號，點進去有完整摘要 + 原始來源連結。對每個 `#數字` 區塊逐一比對 Step 3 的三層關鍵字。

---

## Step 3｜關鍵字過濾

### 第一層（核心興趣，優先收錄）

| 關鍵字 | 範疇 |
|--------|------|
| `Google` / `Gemini` / `DeepMind` | Google AI 全線 |
| `OpenAI` / `GPT` / `ChatGPT` | OpenAI |
| `Anthropic` / `Claude` | Claude 系列 |
| `MiniMax` | MiniMax |
| `OpenClaw` | OpenClaw 生態 |

### 第二層（主要競爭者，一般收錄）

| 關鍵字 | 範疇 |
|--------|------|
| `Meta` / `Llama` | Meta / Llama |
| `Microsoft` / `Copilot` | Microsoft AI |
| `xAI` / `Grok` | xAI |
| `Mistral` | Mistral |
| `DeepSeek` | DeepSeek |
| `Hugging Face` | 開源生態 |
| `NVIDIA` | GPU / CUDA |
| `Apple` | Apple Intelligence |

### 第三層（廣義重大事件，選擇性收錄）

| 關鍵字 | 收錄條件 |
|--------|----------|
| `開源` / `open source` | 重大模型或工具開源 |
| `agent` / `智能體` | agent 架構突破 |
| `多模態` / `multimodal` | 跨模態重大進展 |
| `推理` / `reasoning` | 推理能力研究 |
| `benchmark` | 重要評測結果 |

### 跳過條件（須同時滿足）

1. 第一層完全無命中
2. 第二層命中 < 2 條
3. 第三層命中 = 0

三者同時成立 → 寫「今日無可寫」執行摘要並 `exit 1`。

否則：正常寫文（若命中條目 < 3 走 Light Issue）。

---

## Step 4｜AI 讀取 + 擴充

1. 讀完所有過濾後的條目，建立整體畫面
2. 若細節不夠，`web_search` 找 TechCrunch / 官方部落格 / 原始論文
3. 每個主題至少補 1 個原始來源（官方公告 / 原論文 / 官方文件）
4. 把同一事件的多個來源合併成一個主題
5. 對至少一個關鍵事實做交叉比對（價格、日期、模型名、benchmark、融資額）

---

## Step 5｜寫作

繁體中文。套用 base 風格規則。目標字數預設 **1500–2200 字**。結構：

```markdown
## 今日觀察

一段總結性開場（3–5 句，具體事件切入，不寫「隨著 AI 的快速發展」）。

---

## 主題一 — 副標

2–4 段，消化後的觀點 + 數據 + 為什麼重要。用自己的話，不抄橘鴉原文。至少補一段背景或比較。

---

## 主題二 — 副標

同上。

---

## 主題三 — 副標

同上。

---

## 其他值得關注

- **主題**：一句話摘要 + 為什麼值得注意
- **主題**：一句話摘要 + 為什麼值得注意

---

## 參考連結

- [原始來源](URL)
- [官方公告](URL)
```

**注意**：橘鴉的摘要是簡體中文，全部改寫成繁體中文（視頻→影片、软件→軟體、硬盤→硬碟、运营→營運）。不要留下任何簡體殘留。

每個主題都至少回答：
- 發生了什麼
- 為什麼現在重要
- 對開發者 / 產業意味著什麼
- 它跟最近的同類事件有什麼不同

### Frontmatter

```yaml
---
title: "AI 新聞精選｜YYYY 年 M 月 D 日"
description: "一句話概述今日最重要進展"
publishDate: "YYYY-MM-DDT12:00:00+08:00"
updatedDate: "YYYY-MM-DDTHH:MM:00+08:00"
tags: ["具體公司", "具體產品"]
series: "daily-ai-report"
seriesOrder: N
draft: false
---
```

---

## Step 6｜交給 base 的 Pipeline

套用 `_blog-publisher-base/SKILL.md` 的 Pipeline Step A → F。

**若同一天已有 `YYYY-MM-DD-ai-news-daily.md`**（例如人工補發或重跑）→ 改寫成 `-v2.md`、`-v3.md` 遞增，保留歷史版本。

執行摘要：

```
daily-ai-report 完成

日期：YYYY-MM-DD
slot：12:00 (YYYY-MM-DDT12:00:00+08:00)
橘鴉 issue：issue-N
命中條目：N（第一層 X / 第二層 Y / 第三層 Z）
主題數：N
檔案：YYYY-MM-DD-ai-news-daily.md
封面：已生成 / 跳過
自檢：L1 ✅ / L2 ✅ / L3 ✅ / L4 ✅
build：通過
push：成功
```

---

## Light Issue 與跳過

- 命中條目 < 3 → Light Issue，短版也要寫到 **1000–1400 字**，commit 加 `[light-issue]`
- 三層關鍵字完全不命中 → 寫執行摘要「今日無可寫」+ `exit 1`
- 橘鴉當天還沒發 issue → `exit 1`
