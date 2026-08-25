# CotaUtility.CotaPerformanceCounter / CotaUtility.CotaHealthCheckCore

兩個模組搭配使用:CotaPerformanceCounter 提供監控資訊跟可擴充的檢查介面
(`ICheckProvider`),CotaHealthCheckCore 是建在其上、給 ASP.NET Core 用的健康檢查端點
包裝。目標 netstandard2.0(PerformanceCounter)/ netcoreapp3.1+ 且**僅支援 .NET Core
Web 應用程式**(HealthCheckCore)。

## 偵測特徵

- 專案裡有自己刻的 `/health`、`/api/xxx/GetProjectInfo`、`/api/xxx/CheckXxx` 之類的
  健康檢查/監控 Controller,回傳自訂 JSON 格式
- 手動組裝 CPU/記憶體/組件版本等監控資訊的程式碼

## 是否已用 CotaUtility

- `.csproj` 有 `CotaUtility.CotaPerformanceCounter` 和/或 `CotaUtility.CotaHealthCheckCore`
- `Startup.ConfigureServices`/`Program.cs` 有
  `services.AddHealthChecks().AddCotaCheckAlive()...`
- `UseEndpoints` 裡有 `endpoints.MapCotaCheckAlive()` 等

## 已用時的正確用法檢查清單

- [ ] 路由註冊(`MapCotaCheckAlive`/`MapCotaCheckProjectInfo`/`MapCotaCheckExtraServices`)
      是否寫在 `MapControllerRoute`/`MapControllers` **之前**(文件明確要求順序,寫在後面
      不會生效)
- [ ] 若專案有需要檢查額外服務(例如特定 DB 連線),是否有傳入
      `ICheckProvider[]` 給 `AddCotaCheckExtraServices`,而不是留空——留空的話該路由只會
      回空陣列,等於沒在檢查
- [ ] 若專案同時用 `CotaRedisLog.Serilog`,是否已設定
      `GetLevelHelper.ExcludeHealthCheck()` 排除健康檢查請求的 Log 雜訊(見
      `references/cota-redis-log.md`)
- [ ] 若專案有全域驗證(例如 Windows Negotiate 的 FallbackPolicy
      `RequireAuthenticatedUser`),`MapCotaCheckProjectInfo`/
      `MapCotaCheckExtraServices` 是否已加 `.AllowAnonymous()`——看板後端(svrotr)
      來 ping 不帶 Windows 驗證,沒放行的話看板會顯示 401

## 接入資訊看板[專案監控](警告系統)的完整規格

這兩個端點的真正用途:資訊看板後端定時 ping 專案,異常時自動**推播訊息 + 語音告警**
(語音在推播後 ping 頻率×3 分鐘撥放)。接入時除程式碼外還有以下非程式碼事項:

- **CPU/RAM 權限**(找系統組):`ProcessInfo` 的 CPU/RAM 需要較高權限才取得到值,把執行
  帳號加入 `Performance Monitor Users`(IIS 部署則是把 `IIS AppPool\應用程式集區名稱`
  加入該群組);設定後 `iisreset /restart` 即可,不用重開機。權限沒設定的話看板 CPU/RAM
  欄位會顯示 `*` 號。
- **註冊看板**:API 做完後自行登入資訊看板管理後台
  https://prjchartsserver.cotabank.com/cotaProj(AD 帳密)→「專案監控清單」設定,提供
  URL、ping 頻率(單位**分鐘**,針對額外服務 API)、專案中文名稱。
- **JSON 規格**(swagger 文件要求):欄位無值時**不可回 null**——字串回 `""`、JSON 物件回
  `{}`、陣列回 `[]`。
- **`ErrorMessage` 會被語音念到**:IsOk=false 時看板語音告警會唸這個欄位,分隔不要用
  空白(會擠在一起),用句號/逗號。
- **`ICheckProvider.GetCheckResults` 是同步簽章**,做不了 async 檢查(例如 async DB 查詢);
  需要 async 的檢查項只能放進 ASP.NET Core 的 `IHealthCheck`(自訂 `/health` 端點),
  不要硬塞進 `ICheckProvider`。
- **`AddCotaCheckExtraServices` 在註冊期(Build 前)就要拿到 `ICheckProvider` 實例**,但
  檢查邏輯常需要 DI 解析的 singleton——用一個 lazy wrapper(請求期才從正式 app 的
  `IServiceProvider` 解析)解決;不要在 Build 前 `BuildServiceProvider()`,會造成
  singleton 雙實例。
- **`CheckItem` 的 `ProjectName` 是 protected**,子類別裡要用字串常數,不能引用自己的
  `ProjectName` 屬性。

## 未用時的替換建議

`CotaPerformanceCounter` 類別方法都是**靜態呼叫**:

```csharp
// 單獨使用 CotaPerformanceCounter(不透過 HealthCheckCore 的路由包裝時)
[HttpGet("[action]")]
public string GetProjectInfo()
{
    try
    {
        var info = CotaPerformanceCounter.GetMonitorInfo(Assembly.GetExecutingAssembly());
        return CotaPerformanceCounter.ResponseJson(info);
    }
    catch (Exception e)
    {
        return CotaPerformanceCounter.ResponseJson(e.Message);
    }
}

[HttpGet("[action]")]
public string GetExtraService()
{
    // MSSqlChecker 是套件內建、現成可用的 ICheckProvider 實作,檢查指定 DB 連線是否正常
    var checkers = new List<ICheckProvider> { new MSSqlChecker("eLoan", new List<string> { "eLoan" }) };
    var results = CotaPerformanceCounter.GetCheckResults(checkers);
    return CotaPerformanceCounter.ResponseJson(results);
}
```

`GetMonitorInfo` 回傳的 JSON 結構包含 `SiteName`、`ProcessInfo`(Id/Name/StartTime/
ThreadInfo/Cpu/Ram/Is64BitProcess)、`EnvironmentInfo`(UserName/MachineName/
ClrVersion/DotNetCoreVersion)、`HelperInfo`(套件版本)。`GetCheckResults` 回傳陣列,
每筆含 `Title`/`IsOk`/`ErrorMessage`/`Description`/`LastCheckTime`。

若走 `CotaHealthCheckCore` 的整合路由包裝(推薦,免自己寫 Controller):

```csharp
// ConfigureServices
var checkers = new List<ICheckProvider>
{
    new MSSqlChecker("EasyLoan", new List<string> { "PhoneTransfer" })
};
services.AddHealthChecks()
    .AddCotaCheckAlive()
    .AddCotaCheckProjectInfo()
    .AddCotaCheckExtraServices(checkProviders: checkers);

// Configure -> UseEndpoints(要寫在 MapControllerRoute/MapControllers 之前)
endpoints.MapCotaCheckAlive();               // 預設 /health
endpoints.MapCotaCheckProjectInfo();         // 預設 /api/MonitorInfos/GetProjectInfo
endpoints.MapCotaCheckExtraServices();       // 預設 /api/CheckItems/GetExtraServices
```

路由可以重複註冊到不同 pattern(例如舊 HAProxy 設定用 `/alive`,新的想統一成
`/health`,可以兩個都註冊,不用改 HAProxy 設定)。

## 適用情境提醒

`CotaHealthCheckCore` 僅支援 .NET Core Web 應用程式,舊 .NET Framework 專案裝不了,
只能考慮單獨用 `CotaPerformanceCounter` 取得監控資訊,自己接健康檢查路由。

## 參考

- CotaPerformanceCounter: https://svrconf.cotabank.com/pages/viewpage.action?pageId=94569376
- CotaHealthCheckCore: https://svrconf.cotabank.com/pages/viewpage.action?pageId=98762990
- 【資訊看板2】[專案監控]API說明: https://svrconf.cotabank.com/pages/viewpage.action?pageId=102237020
- 【資訊看板(2)】[專案監控]Q&A(401/ping 頻率/語音規則): https://svrconf.cotabank.com/pages/viewpage.action?pageId=43745499
- 專案監控-圖例及說明: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82509905
- 輔助 DLL: https://svrconf.cotabank.com/pages/viewpage.action?pageId=102237026
- API JSON 規格(swagger): http://192.168.251.169/MonitorInfoDemo/swagger/
