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
