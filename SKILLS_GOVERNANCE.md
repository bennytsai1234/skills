# Skills Governance & Management Guide (技能治理與管理規範)

## 核心原則 (Core Principles)
1. **唯一真實來源 (Single Source of Truth)**: `~/skills/` 是所有技能的 Canonical Source。禁止在工具目錄（如 `~/.openclaw/workspace/skills/`）內直接修改或新增長期維護的技能。
2. **結構完整性 (Structural Integrity)**: 所有技能必須以「目錄」形式存在，包含 `SKILL.md` 及其相關腳本與 metadata。禁止將單一檔案散放於目錄外。
3. **路徑無關性 (Path Independence)**: 內部引用路徑應優先使用相對於 `~/skills/` 的 Canonical Path，而非工具特定的舊路徑。

## 目錄結構 (Directory Structure)
- `~/skills/`: 唯一保留的技能目錄，放置跨工具可重用的通用技能。
- 工具本地目錄僅保留相容層或狀態資料，不再在 `~/skills/` 下額外維護 `tooling/` 或 `vendor/` 分層。

## 新增技能流程 (Adding New Skills)
1. 在 `~/skills/` 對應的分類目錄（如 `shared/`）下建立新目錄。
2. 完成開發後，在受影響工具的 `skills/` 相容層建立軟連結 (symlink)。
   - 例如: `ln -s ~/skills/my-new-skill ~/.openclaw/workspace/skills/my-new-skill`
3. 確保將變更提交至 `~/skills/` 的 Git 倉庫。

## 相容性維護 (Compatibility Layer)
- 工具目錄下的 `skills/` 資料夾僅作為「掛載點」。
- 若工具不支援自訂目錄，則在此處建立指向 `~/skills/` 的軟連結。
- 若工具支援自訂路徑（如 Hermes `config.yaml`），應優先使用設定檔進行對接。

---
*Last Updated: 2026-04-13*
