# CotaNuGet 與 BaGetter 私有來源設定

`CotaUtility` 系列套件不在 `nuget.org`。目前 NuGet 用戶端可能同時需要兩類內部來源：

- **BaGetter**：`https://ctbaget.cotabank.com/v3/index.json`。開發者端可只連 BaGetter 取得公開套件；BaGetter 是否能提供特定內部套件，仍要以伺服器實際發布/快取狀態為準。
- **CotaNuGet**：內部 UNC 檔案來源，存放 Cota 歷史或特殊版本，作為 BaGetter 尚未承載 Cota 內部套件時的來源。不要因為導入 BaGetter 就自動停用它。

來源切換是 NuGet 用戶端與設定檔的變更，不等於升級 `CotaUtility` 套件版本。要升級套件仍須另行確認版本異動與 breaking change。

## CotaNuGet 路徑

目前已知文件有不同路徑，不能自行猜測或直接把文件範例互相替換：

- 較新環境常見：`\\192.168.251.238\data\CotaNuGet`
- 舊文件曾記載：`\\192.168.233.237\data\CotaNuGet`
- BaGetter 教學中的 `\\nas\data\CotaNuGet` 是該文件環境的顯示值，不代表所有機器都應改成此路徑

實際使用前以現有專案的 `NuGet.Config`、目前可連線的來源或系統組確認為準。若 Cota 內部套件 Restore 失敗，先確認 UNC 路徑與來源是否仍啟用，不要先判定 BaGetter 壞掉或直接改套件版本。

## NuGet 設定檔優先順序

NuGet 執行時會合併多份 `NuGet.Config`，後者覆寫前者：

1. 電腦層級：`%ProgramFiles(x86)%\NuGet\Config\*.config`
2. 使用者層級：`%AppData%\NuGet\NuGet.Config`
3. 方案/專案層級：從方案根目錄向上搜尋的 `NuGet.Config`

因此修改 Visual Studio 使用者設定後，仍要檢查方案/專案目錄是否有覆寫來源；CI/建置主機也不能只假設使用開發者的使用者設定。

## 建議來源狀態

一般內部 .NET 專案的目標狀態：

- `BaGet`/`BaGetter`：啟用，端點為 `https://ctbaget.cotabank.com/v3/index.json`
- `CotaNuGet`：在仍有內部 Cota 套件未搬遷或未確認前保持啟用
- `nuget.org`：在公司要求所有客戶端流量經 BaGetter 時停用，不必刪除來源；保留來源可在維護時恢復
- `LocalBaGet`：沒有本機 BaGetter 容器時停用
- Visual Studio Offline Packages：依專案需要保留

顯示名稱可依既有設定使用 `BaGet` 或 `BaGetter`；名稱不是伺服器端點，重點是 URL 與來源是否有效。

## 設定步驟

1. 先列出目前生效來源：

   ```powershell
   dotnet nuget list source
   dotnet nuget locals all --list
   ```

2. 在 Visual Studio「工具 → 選項 → NuGet 套件管理員 → 套件來源」新增或啟用 BaGetter，並確認 CotaNuGet 的實際 UNC 路徑。

   CLI 也可使用：

   ```powershell
   dotnet nuget add source https://ctbaget.cotabank.com/v3/index.json -n BaGet
   dotnet nuget disable source nuget.org
   ```

   若來源已存在，先檢查實際設定，不要重複新增或把仍在使用的 CotaNuGet 路徑覆蓋掉。

3. 來源切換後若遇到舊快取、來源混用或版本不一致，再清除快取並強制 Restore：

   ```powershell
   dotnet nuget locals all --clear
   dotnet restore --force --no-cache
   ```

   清除 `global-packages` 會影響本機所有 .NET 專案；共用建置主機應先評估影響。

4. 驗證：

   ```powershell
   dotnet nuget list source
   dotnet restore --configfile "$env:APPDATA\NuGet\NuGet.Config"
   ```

   Restore 日誌中，客戶端對公開套件的直接連線應指向 BaGetter；Cota 內部套件若尚未發布到 BaGetter，應仍能由已確認的 CotaNuGet 來源取得。

## Proxy 與憑證

NuGet 的 Proxy 設定與 Node/npm 的 Proxy 設定是不同用戶端設定，不能把 Verdaccio 教學中的 `npm config` 指令直接套用到 NuGet。

若環境仍需 Proxy，依公司網路規則設定 `http_proxy`、`https_proxy`，並將公司內部網域加入 `no_proxy`，避免 BaGetter 或 UNC 相關流量被錯誤導向外部 Proxy。不要為了排錯而關閉 TLS 驗證。

## CI/CD 與建置主機

CI/CD 不應依賴某位開發者的 `%AppData%\NuGet\NuGet.Config`。應確認建置主機的有效設定、BaGetter 可連線、CotaNuGet UNC 權限與來源優先順序；需要時以 `--configfile` 明確指定受控設定檔。

`NuGet.Config` 若含 `<packageSourceCredentials>`，不得把明文密碼簽入版本控制；使用建置系統的 Secret 或環境注入。

## 範圍界線

本 reference 只描述 .NET/NuGet。Verdaccio 文件的 `npm registry`、`npm config` 與 `NODE_OPTIONS` 屬於 Node/npm 開發環境，不應當作 Cota NuGet 套件升級或 NuGet 設定步驟。
