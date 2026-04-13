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

依來源類型決定策略：

### 來源是 AI 對話摘要（Gemini/ChatGPT）

**必須重構成「技術解析」格式**，不能直接發：

```markdown
## 這篇文章在說什麼

1–2 段，用自己的話解釋文章在做什麼。

## 為什麼重要

技術或方法的價值，對誰有幫助，解決了什麼問題。

## 技術細節

核心方法、關鍵工具、數據支撐。

## 我的觀點

消化後的判斷，可以正面或批評，要有觀點。

## 參考連結

- [原文標題](URL)
```

### 來源是有結構的技術文（正規部落格、論文解析）

保留原有結構，只做格式清理 + 繁中化 + 禁用詞替換（套用 base 的 L1 掃描）。

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

套用 `_blog-publisher-base/SKILL.md` 的 Pipeline Step A → F。

封面圖一樣走 `gen_cover.py`，失敗不阻斷發布。

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
