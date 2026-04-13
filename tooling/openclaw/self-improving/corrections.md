# Corrections Log

## 2026-03-25 - Edit Tool Text Mismatch

**CONTEXT:** 使用 `edit` 工具編輯 MEMORY.md 時，嘗試用 oldText 匹配一段文字但失敗

**ISSUE:** 
- 第一次 edit 成功（路徑替換）
- 第二次 edit 成功（路徑替換）
- 第三次 edit 失敗，因為 oldText 包含 `\n` 換行符，但實際檔案內容的換行方式與預期不符

**LESSON:** 
使用 `edit` 工具前，務必先 `read` 檔案取得**完全精確**的文字（包括所有空白、換行、縮排）。
千萬不要自己猜測或重構 oldText，必須用 `read` 取得實際內容。

**CORRECT WORKFLOW:**
```
1. read(path) → 取得檔案目前內容
2. 從 read 結果複製精確的 oldText
3. edit(path, oldText, newText)
```

**TAGS:** #tool-use #edit-tool #best-practice
