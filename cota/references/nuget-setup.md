# CotaNuGet 私有來源設定

CotaUtility 系列套件不在 nuget.org,是透過內部私有 NuGet 來源(UNC 檔案共享路徑)發佈。

**待確認**:目前查到兩個不同時期文件記載的路徑,不確定哪個目前有效,套用前請跟系統組
或現有專案的 NuGet.config 核對:

- `\\192.168.251.238\data\CotaNuGet`(來源:「NuGet環境設定 (CotaNuGet)」頁,較新)
- `\\192.168.233.237\data\CotaNuGet`(來源:「.Net Core 專案建置指引」頁,內容仍是
  VS2019 / .NET 5 時期寫的,可能已過期)

## 設定步驟(Visual Studio)

1. 工具 → 選項 → NuGet 套件管理員 → 套件來源
2. 新增一組來源:名稱 `CotaNuGet`,來源填上方確認過的 UNC 路徑
3. 確定後,在專案按右鍵「管理 NuGet 套件」,套件來源切換成 `CotaNuGet`,即可看到
   目前提供的套件清單並安裝。

## 版本管理提醒

CotaUtility 套件版本更新頻繁(例如 CotaDB 在觀察期間內就有 1.0.0→1.0.3 的功能異動),
正式環境安裝時建議鎖定明確版本號,不要用浮動版本,更新前看一下該套件 Confluence 頁的
版本異動說明(尤其注意有沒有 breaking change)。
