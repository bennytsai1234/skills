---
name: source-security-audit
description: "對任一程式碼庫執行全面源碼安全稽核（A–E：相依漏洞、SAST、機密外洩、人工稽核），並提供修補劇本。針對銀行管控 Windows 環境調校。當使用者要求源碼安全檢查、安全稽核、漏洞掃描、機密外洩檢查時使用。"
---

# 源碼安全稽核（A–E，泛用）

工具掃描 + 人工稽核的完整流程，適用任一程式碼庫。為**銀行管控 Windows 環境**調校，已內建常見雷區。所有掃描輸出寫到 scratchpad，不污染 repo；安裝類動作先說明再執行。

## 0. 先偵測技術棧
先看 repo 根目錄決定走哪條指令：
- `*.csproj` / `*.sln` → .NET（A 用 `dotnet`，C 用 Security Code Scan）
- `package.json` → Node（A 用 `npm audit` / `pnpm audit`）
- `requirements.txt` / `pyproject.toml` → Python（A 用 `pip-audit`）
- `go.mod` → Go（A 用 `govulncheck`）
- B（DevSkim）、D（Gitleaks）、E（人工稽核）與技術棧無關，一律適用。

## 環境雷區（先讀，省去重蹈覆轍）
- **Semgrep 無原生 Windows 支援**（需 Docker/WSL）→ SAST 改用 **DevSkim**（多語言）。
- **DevSkim 需 .NET 9 runtime**，若本機只有其他版本 → 執行前設 `$env:DOTNET_ROLL_FORWARD='Major'`（零安裝跑在更高版本上）。
- **銀行防毒會攔截「記憶體組裝 + 含金鑰字樣」的 PowerShell 腳本**（ParserError: malicious content）→ 解析掃描結果（SARIF/JSON）一律改用 **Python**，不要在 PS 裡 ConvertFrom-Json 大型含密內容。
- **winget 的 msstore 源因 SSL 檢查憑證不符會失敗** → 安裝套件加 `--source winget`。
- **資料夾含多個專案檔/產物** → 指定單一專案檔，避免歧義錯誤。
- **LTS 框架**：相依「過期」報告常把下一個大版本當「最新」；**留在現行 LTS 系列、勿盲目跳大版本**。
- 安裝類動作（pip/winget/dotnet tool/npm -g）依環境政策先說明再裝；不擅改全域 npm/git 設定，不做 strict-ssl false 之類不安全繞過。

---

## A — 相依套件漏洞（多為免安裝）
- .NET：`dotnet restore <proj>` → `dotnet list package --vulnerable --include-transitive` → `dotnet list package --outdated`
- Node：`npm audit --omit=dev`（或 `pnpm audit` / `yarn npm audit`）
- Python：`pip-audit`
- Go：`govulncheck ./...`

判讀：High/Critical 優先；若漏洞**無修補版**，評估實際可達性（攻擊面是否能被不可信輸入觸發、該元件是否用於正式路徑）再定優先序，別只看 CVSS。

## B — SAST（DevSkim，多語言）
```bash
# 安裝（一次）：dotnet tool install --global Microsoft.CST.DevSkim.CLI
SP=<scratchpad>; DEVSKIM="$HOME/.dotnet/tools/devskim.exe"
DOTNET_ROLL_FORWARD=Major "$DEVSKIM" analyze -I . -O "$SP/devskim.sarif" -f sarif \
  -g "**/bin/**" "**/obj/**" "**/node_modules/**" "**/dist/**" "**/build/**" \
     "**/publish/**" "**/vendor/**" "**/.git/**" "**/*.min.js" "**/lib/**"
```
用 Python 解析、過濾第三方/產物雜訊，只看自家程式碼 findings：
```python
import json
j=json.load(open(f"{SP}/devskim.sarif",encoding="utf-8")); run=j["runs"][0]
rules={r["id"]:r.get("name") for r in run["tool"]["driver"]["rules"]}
skip=("node_modules","vendor","dist","build","publish","\\lib\\","/lib/",".min.js",".vs")
for r in run["results"]:
    u=r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    if any(s in u for s in skip): continue
    print(u, rules.get(r["ruleId"]))
```
常見誤判：字串裡的關鍵字（如 CSP 的 `'unsafe-inline'` 被當 `unsafe`）、xmlns 的 http URL。逐一確認再列入。

## C — 語言專屬深掃（選用）
- **.NET**：暫時把 `SecurityCodeScan.VS2019`（`<PrivateAssets>all</PrivateAssets>`）加進專案 → `dotnet build` 抓 `SCS####` 警告 → **掃完還原專案檔**，不留改動。
- **Node/TS**：`semgrep --config p/owasp-top-ten`（若可用）或 ESLint security plugins。
- **Python**：`bandit -r .`。

## D — 機密外洩（Gitleaks）
```bash
# 安裝（一次）：winget install --id Gitleaks.Gitleaks --source winget
gitleaks detect --source . --report-path "$SP/gitleaks.json" --no-banner
```
重點查 git **歷史**（檔案即使已刪仍留存）：
```bash
git log --all --diff-filter=A --pretty=format: --name-only \
  -- "*.db" "*.sqlite" "*.pem" "*.key" "*.pfx" "**/dp-keys/*" "*.env" "appsettings*.json" | sort -u
```
加重風險：加密金鑰圈 + 含「加密憑證/金鑰」的資料檔若**同在歷史** → 可被一併還原成明文。

## E — 人工稽核（工具盲點，通用清單）
逐項檢查並對照「應有的不變量」，發現偏離才是問題：
- **認證/授權**：每個端點是否有驗證；異動動作是否有角色/權限檢查；是否有「免登入/萬能管理員」的後門模式且可能誤啟用於正式環境。
- **CSRF**：狀態變更端點是否有防護（token / SameSite）。
- **SSRF / 資料外送**：對外 HTTP 呼叫的目標 URL 是否可被使用者控制；失敗 fallback 是否送往寫死的第三方端點而外洩 prompt/憑證。
- **機密存放**：API 金鑰/密碼是否加密儲存、用完即丟，而非明文落庫或寫入設定檔。
- **錯誤洩漏**：正式環境是否回傳堆疊/例外細節；告警 webhook 是否帶 StackTrace/QueryString 外送。
- **輸入驗證 / 反序列化**：是否用安全的解析器、避免多型/型別名稱反序列化、有長度與結構驗證。
- **傳輸/標頭**：HSTS、HTTPS 重導、安全標頭、CSP 是否過寬（`'unsafe-inline'`）。

---

## 報告格式
依嚴重性分 🔴高 / 🟠中 / 🟡低；每項給「位置 + 為何是問題 + 修補」。另列「✅ 做得好的部分」避免只報壞消息。最後給「我能做 / 需你做（如金鑰輪換、破壞性操作）」的下一步。

## 修補劇本

### 清理 git 歷史中的機密（破壞性，務必分步確認）
```bash
# 0) 先輪換已外洩的憑證/金鑰（通常只有使用者能在後台做）
pip install git-filter-repo                                      # 一次
git bundle create ../backup-$(date +%Y%m%d-%H%M%S).bundle --all  # 備份！
git bundle verify <backup>                                       # 驗證可還原
GFR=$(python -c "import git_filter_repo;print(git_filter_repo.__file__)")
python "$GFR" --invert-paths --path <敏感路徑> --path-glob '<glob>' --force
git log --all --pretty=format: --name-only -- "<敏感路徑>" | sort -u   # 驗證殘留為空
```
**force-push 是不可逆對外操作，務必先取得使用者明確同意**：
```bash
git remote add origin <url>      # filter-repo 會移除 origin，需重加
git push origin --force --all && git push origin --force --tags
```
推後提醒：① 遠端（如 GitHub）仍可能短期保留懸空 commit → 憑證當作已外洩；② 他人 clone 過的副本需重新 clone；③ 把敏感路徑加進 `.gitignore` 以防再犯。

### 相依漏洞
能升版就 pin 已修補版（留在現行 LTS 系列），重跑 A 驗證；無修補版則記「追蹤待修」並評估可達性。

### 注意事項
- 暫時為掃描修改專案檔（如加 analyzer）後，**務必還原**，不把掃描用的相依留在 repo。
- 行為性的強化（關閉某 fallback、收緊 CSP、加認證防呆）可能影響運行中系統，**先確認使用者用法再改**，必要時做成可設定且預設安全。
