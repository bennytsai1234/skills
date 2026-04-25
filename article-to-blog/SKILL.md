---
name: article-to-blog
description: 將外部來源的技術文章（Gemini/ChatGPT 對話導出、他站部落格、論文解析…）清理並發布至 openclaw-blog。非排程，按需觸發。繼承 _blog-publisher-base。
---

# article-to-blog

按需觸發的「外部文章→部落格」整理流程。用途：

- 收到 Telegram 附件（Gemini/ChatGPT 對話 markdown 導出）
- 貼文轉發，要求整理後發到部落格
- 把他站文章整理成「技術解析」格式

風格規則、schema、L1–L4 自檢、發佈管線全部繼承 `_blog-publisher-base/SKILL.md`。

---

## Variant 變數

```
SLOT_ID       = <動態 slug，Step 3 決定>
PUBLISH_HHMM  = <執行當下 HH:MM，見下方說明>
COVER_TITLE   = <文章標題>
COVER_TAGS    = <從 tags 取前 3 個，逗號分隔>
COMMIT_PREFIX = docs: 技術解析
SERIES        = (通常空，除非使用者明確指定系列)
```

### PUBLISH_HHMM 決定規則

article-to-blog **不是定時發文**，所以 `publishDate` 用執行當下的時間到分鐘：

```bash
PUBLISH_HHMM=$(TZ=Asia/Taipei date +%H:%M)
```

Base 的 Pipeline Step B 會組出 `YYYY-MM-DDTHH:MM:00+08:00`。`updatedDate` 同樣是執行當下（兩者相等是預期行為）。

---

## Step 1｜確認文章來源

可能來源：

- **Telegram 附加檔案**：`~/.openclaw/media/inbound/` 下，依檔名或時間戳找
- **對話直接貼文**：直接取 message 文字
- **現有檔案**：若使用者指名某個 `.md` 檔案

寫檔前先比對 `~/projects/openclaw-blog/src/content/post/` 是否已有同主題文章。

---

## Step 2｜清理（Clean）

在轉換前先做來源可信度判讀：

- **原始技術來源**：官方部落格、原論文、原始 repo、原始文件頁面
- **次級來源**：媒體報導、整理文章、AI 對話導出

若來源是次級來源，後續 Step 4 必須補至少 1 個原始來源，不可直接拿二手摘要改寫成 blog。


移除以下多餘內容，只保留乾淨的文章主體：

| 類型 | 範例 |
|------|------|
| AI 對話浮水印 | `*Exported from [Voyager](...)*`、`*Generated on...*` |
| 對話框架文字 | `Turn 1`、`### 🤖 Assistant`、`### Human` |
| 時間戳與元資料 | `**Date**: April 3, 2026`、`**Turns**: 1`、`**Source**: [Gemini Chat]` |
| Markdown 標題裝飾 | `# Turn 1`、`## Turn 2`（保留文章真正的一級標題） |
| 空行與錯誤區塊 | 連續空行、格式錯誤 code fence |
| 重複的 frontmatter | 若檔案已含 frontmatter 且格式正確可保留，但會在 Step 4 統一覆寫 |

**保留**：

- 所有技術內容（正文、表格、code block）
- 章節結構（`##` 開始）
- 圖片連結（需確認是外部有效連結）

---

## Step 3｜決定 slug 與標題

slug 規則：標題英文化，全小寫，空格換 `-`：

- 「Gemma 4 稠密 vs MoE 深度解析」→ `gemma-4-dense-vs-moe`
- 「P-GRPO 偏好對齊」→ `p-grpo-preference-alignment`

組出：

```bash
SLOT_ID="<english-slug>"
```

同日有同 slug 檔案 → 加 `-v2` / `-v3` 遞增。

---

## Step 4｜轉換格式（Transform）

先做研究補強，再動筆：

1. `web_fetch` 原始文章 / 附件內容
2. `web_search` 找官方來源、作者背景、相關報導
3. 若是論文 / 開源專案，再找論文頁或 repo README
4. 對至少 1 個關鍵事實做交叉比對（數字、時間、價格、模型名、benchmark）

沒有補強研究之前，不要直接開始寫。


依來源類型決定策略：

### 來源是 AI 對話摘要（Gemini/ChatGPT）

**必須重構成「技術解析」格式**，不能直接發。目標字數預設 **1200–1800 字**；若素材足夠，優先寫到 1800+。

```markdown
## 這篇文章在說什麼

1–2 段，用自己的話解釋文章在做什麼。

## 背景脈絡

這件事出現之前，業界原本怎麼做。這次的新東西補了哪個洞。

## 為什麼重要

技術或方法的價值，對誰有幫助，解決了什麼問題。

## 技術細節

核心方法、關鍵工具、數據支撐。

## 跟既有做法相比

至少拿一個相關模型 / 工具 / 方法來比較，講出差異。

## 我的觀點

消化後的判斷，可以正面或批評，要有觀點。

## 參考連結

- [原文標題](URL)
```

### 來源是有結構的技術文（正規部落格、論文解析）

保留原有結構，只做格式清理 + 繁中化 + 禁用詞替換（套用 base 的 L1 掃描）。

但不要只做翻譯。至少補以下其中兩項：
- 原作者沒展開的背景脈絡
- 跟同類工具 / 論文的比較
- 對工程實務的影響
- 你自己的判斷

目標字數預設 **1200–2000 字**。

### Frontmatter（統一覆寫）

```yaml
---
title: "【技術解析】具體標題"
description: "一句話描述文章核心價值"
publishDate: "YYYY-MM-DDTHH:MM:00+08:00"   # 執行當下
updatedDate: "YYYY-MM-DDTHH:MM:00+08:00"   # 執行當下
tags: ["具體技術", "具體工具"]
draft: false
---
```

---

## Step 5｜交給 base 的 Pipeline

正式交給 base 之前，做這個最終檢查：

- 有沒有至少 1 個原始來源 + 2 個側面來源
- 有沒有「背景脈絡」和「跟既有做法相比」
- 有沒有至少一段作者判斷
- 字數是否夠長、但不是灌水
- **是否為繁體中文**：發布前必須閱讀全文，確認無簡體字後再發布

## 繁體中文檢查流程（手動核對）

發布前必須：

1. **完整閱讀文章**：用 read 工具讀取整篇文章內容
2. **人工確認**：親自用眼睛檢查每一段是否為繁體中文
3. **若有簡體字**：當場修正後再繼續流程
4. **確認無誤**：確定都是繁體中文才能執行 build + push

**不要使用 grep 或自動腳本來掃描——就是要你親自讀過確認。**

套用 `_blog-publisher-base/SKILL.md` 的 Pipeline Step A → F。

封面圖直接由 Agent 展開 prompt 後呼叫 `gemini_generate.py`（同 base Pipeline Step C），失敗不阻斷發布。

執行摘要：

```
article-to-blog 完成

來源：<Telegram 附件 / 對話貼文 / 現有檔案>
slug：<english-slug>
檔案：YYYY-MM-DD-[slug].md
時間戳：YYYY-MM-DDTHH:MM:00+08:00
封面：已生成 / 跳過
自檢：L1 ✅ / L2 ✅ / L3 ✅ / L4 ✅
build：通過
push：成功
```

---

## 決策規則

- **直接發布**：來源是乾淨的技術文（正規部落格、論文解析）→ 只做格式清理，保留原結構
- **重構發布**：來源是 AI 對話摘要 → 必須重構成「技術解析」格式
- **已存在**：同日同 slug 檔案已存在 → 評估新舊品質，保留較新或較完整版本，舊版本改 `-v2`

---

## Astro 框架限制與發佈原則

- **限制**：文章標題必須小於 60 字元；遇到 `$` 符號時，必須 escape 為 `\$` 以防止 KaTeX 頁面編譯報錯。
- **發佈原則**：article-to-blog 的 pipeline 僅為參考用，並非硬性規定的聖旨。代理或作者可依循自己的想法和撰寫節奏按需調整，重點在於最終產出的內容與質量，而不必強制死板地執行每一步流程。
