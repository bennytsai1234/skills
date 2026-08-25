# CotaUtility.CotaRedisLog

## 何時適用

需要集中化、結構化 Log 的專案。把 Log 非同步寫入 Redis,透過 Seq(LogServer)介面
統一查詢,取代分散在各主機上的檔案 Log。目標 netstandard2.0。

兩種套件,擇一:
- **CotaUtility.CotaRedisLog.Serilog**——效能較好,**新專案建議用這個**
- **CotaUtility.CotaRedisLog.NLog**——為了支援舊專案而開發,效能相對較差

兩者都實作 `Microsoft.Extensions.Logging.ILogger`,支援結構化 Log(訊息裡用
`{PropertyName}` 帶參數,會自動變成 Log 的 JSON 屬性),內建 Log Forging 防護(自動處理
換行符號)。CLEF(Compact Log Event Format)格式。

## 偵測特徵

- 專案有自訂的 NLog/log4net 設定檔,但寫的是檔案/Console,不是 Redis
- `Console.WriteLine` / 自訂 `Trace.WriteLine` 當作主要 Log 機制
- 已經在用 `Microsoft.Extensions.Logging.ILogger`,但 Provider/Sink 不是指向 Redis
  (例如只掛了 Console/File sink)
- Log 訊息用字串拼接(`$"user {name} did {action}"`)而非結構化參數(`{name}`/`{action}`),
  即使已經接了 CotaRedisLog 也算沒用好

## 是否已用 CotaUtility

- `.csproj` 有 `CotaUtility.CotaRedisLog.Serilog` 或 `.NLog`
- Program.cs/Startup.cs 有 Serilog/NLog 相關 host builder 設定指向這個套件

## 已用時的正確用法檢查清單

- [ ] Log 訊息是否用結構化參數(`logger.LogInformation("user:{@userInfo} login!", userInfo)`)
      而不是字串插值,才能享受到結構化查詢的好處
- [ ] 若專案同時有 `CotaHealthCheckCore`,是否已用
      `CotaUtility.CotaRedisLog.Serilog.GetLevelHelper.ExcludeHealthCheck()` 排除掉
      健康檢查請求的雜訊 Log(見 `references/performance-counter-healthcheck.md`)
- [ ] 例外處理時是否有把 `Exception` 物件傳給 logger(而不是只記字串
      `ex.Message`),才能保留完整 stack trace 到結構化 Log 裡

## Log 等級使用建議(套件文件提供的分類參考)

| 等級 | 用途 |
|---|---|
| Trace | 最細節的訊息,例如使用者的操作軌跡 |
| Debug | 除錯用有用資訊,例如輸入輸出、呼叫 API 的參數 |
| Information | 一般資訊 |
| Warning | 應用程式已處理到的錯誤(例如參數格式不對、IP 不符合被拒絕) |
| Error | 應用程式未預期的錯誤 |
| Critical | 會讓應用程式 Crash 或起不來的錯誤 |

掃描既有專案的 Log 呼叫時,可以順便檢查等級用得合不合理(例如把應該是 Warning 的業務
規則錯誤全部記成 Error,或反過來把真正未預期的例外記成 Information,都會讓之後查 Log
的人難以分辨嚴重程度)。

## 未用時的替換建議

```csharp
// appsettings/Program.cs 大致設定(依官方最新用法為準,此處僅示意)
// 註冊完成後,一般 DI 注入 ILogger<T> 直接寫 Log 即可,寫法跟原生 ILogger 一致:
logger.LogWarning("{functionName}({errorCode}) 發生例外", "TestEx", 9999);
```

結構化 Log 實際落地後是 CLEF(Compact Log Event Format)JSON,除了自訂訊息裡帶的參數
(例如上面範例的 `functionName`/`errorCode`),套件會自動附加
`Application`/`EnvironmentName`/`EnvironmentUserName`/`MachineName`/`ProcessId`/
`ThreadId`/`RequestId`/`RequestPath`/`SourceContext`/`LogVersion` 等欄位,查 Log 時
可以拿這些欄位篩選,不用自己額外加。

## 適用情境提醒

如果專案本來就沒有集中式 Log 需求(例如小型內部工具、單機跑批),維持簡單的
Console/File Log 也可以,不用強推;但只要專案有多實例部署、或需要跨主機查 Log 除錯,
就值得導入。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=94569512

（母頁 CotaRedisLog 分散式高效能Log解決方案:pageId=94569514,另有 Seq 查詢介面說明頁
`LogServer - Seq`）
