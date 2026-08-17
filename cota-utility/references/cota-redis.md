# CotaUtility.CotaRedis

## 何時適用

需要用 Redis 當應用程式的分散式快取(`IDistributedCache`)或 Session 存放區的專案——
典型情境是**專案會部署多台機器 / 需要 HA,或掛在 HAProxy 後面**,不能只靠單機記憶體
(`AddDistributedMemoryCache`/預設 in-memory Session)。目標 netstandard2.0。

## 偵測特徵

- `services.AddDistributedMemoryCache()`
- `services.AddSession()` 搭配
  `services.AddDataProtection().PersistKeysToFileSystem(...)`
- 手刻的 `IMemoryCache` 用法但實際需求是跨機共享狀態(單機 cache 在多機部署下會不一致,
  這是常見的隱藏 bug 來源)
- 自己刻的 Redis pub/sub 邏輯(直接用 `StackExchange.Redis`)

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.CotaRedis"`
- `services.AddCotaRedisCache(...)` / `services.AddCotaRedisSession(...)` /
  `services.AddCotaRedisPubSub()`

## 已用時的正確用法檢查清單

- [ ] 是否用新式的 `environment: RedisEnvironment.Internal/Dmz/BrSys` 參數,而不是舊式
      `isExternalProject: bool`(舊寫法仍可用但文件標示建議遷移到新版)
- [ ] `AddCotaRedisSession` 是否確實**取代**掉原本的
      `AddDistributedMemoryCache()`/`AddDataProtection().PersistKeysToFileSystem(...)`(這兩行應該被註解掉或移除,不是並存)
- [ ] 若有用 `ICotaRedisPubSub`,是否額外呼叫了 `AddCotaRedisPubSub()`(光注入
      Cache/Session 不會自動附帶 PubSub 服務)
- [ ] 遇到 `RedisTimeoutException` 時,是否已核對過 exception 訊息裡的 `clientName`
      跟系統組申請的 Redis 帳號資訊是否一致(這是文件列出的常見問題)

## 未用時的替換建議

```csharp
// 舊寫法
services.AddDistributedMemoryCache();
services.AddDataProtection()
        .PersistKeysToFileSystem(new DirectoryInfo(Configuration["YourFilePath"]))
        .SetApplicationName("YourApplicationName");
services.AddSession();

// 改成(語法幾乎一樣,方法名換掉就好)
services.AddCotaRedisSession(environment: RedisEnvironment.Internal); // 內部專案
// services.AddCotaRedisSession(environment: RedisEnvironment.Dmz);   // 對外(DMZ)
// services.AddCotaRedisSession(environment: RedisEnvironment.BrSys); // 分行系統
```

`IDistributedCache` 注入方式跟原生 ASP.NET Core 一致(`Get`/`SetString`),對開發者
幾乎無痛轉移。

## ICotaRedisPubSub 完整用法(v1.1.0 新增)

```csharp
// 註冊 —— 就算已經有 AddCotaRedisSession/AddCotaRedisCache,PubSub 仍要額外呼叫
services.AddCotaRedisSession();
services.AddCotaRedisPubSub(); // 對外專案一樣要帶 isExternalProject: true 或 environment 參數

// 訂閱(通常放在背景服務 IHostedService 裡)
public sealed class DemoEchoListener : IHostedService
{
    private readonly ICotaRedisPubSub pubSub;
    private IDisposable subscription;

    public DemoEchoListener(ICotaRedisPubSub pubSub) { this.pubSub = pubSub; }

    public async Task StartAsync(CancellationToken ct)
    {
        // SubscribeAsync 第一個參數是 channel 名稱,可自訂
        subscription = await pubSub.SubscribeAsync("demo",
            async (channel, message) => { /* 處理收到的訊息 */ await Task.CompletedTask; },
            ct).ConfigureAwait(false);
    }

    public Task StopAsync(CancellationToken ct)
    {
        subscription?.Dispose();
        return Task.CompletedTask;
    }
}

// 發布
await pubSub.PublishAsync("demo", message, CancellationToken.None).ConfigureAwait(false);
```

## 常見問題排查

`RedisTimeoutException` 通常是 Redis Server 使用者名稱設定錯誤、連不上,拿例外訊息裡的
`clientName` 跟系統組核對申請資訊。要確認測試環境真的有連上 Redis,可在命令提示字元執行
`netstat -ano | find "251.12"`(依實際 Redis Server IP 網段調整關鍵字),看有沒有
`ESTABLISHED` 狀態的連線。

## 前置作業(套用前必須做)

需要先在 Tracko 專案上線申請單跟系統組申請 Redis Server 使用者(帳號=專案名稱轉大寫,
不能有冒號;需指定專案區域:內部/DMZ/核心系統)。這不是程式碼層面能自己解決的,回報時
要提醒使用者這個前置作業。

**這個申請要在開始本機開發/測試前就辦好,不是等上線才辦**:CotaRedis 套件沒有可設定的
connection string,內部直接依 `RedisEnvironment.Internal/Dmz/BrSys` 參數指向銀行內部
真實 Redis Server,**沒有本地端模擬/dev fallback**。也就是說開發機(`dotnet run`/IIS
Express)一樣是連正式的內部 Redis——已驗證的實際案例(`CotaIT2019` 專案)
`appsettings.Development.json` 完全沒有針對 Redis/Session 覆寫任何設定,證實開發環境
與正式環境用的是同一套內部服務。若還沒申請帳號就在本機測 Session/Cache 功能,一樣會
直接噴 `RedisTimeoutException`,不是只有上線後才會遇到。

## 適用情境提醒(專案沒有這個功能時怎麼判斷要不要建議)

如果專案本來就是單機部署、沒有多實例/HA 需求,維持 `AddDistributedMemoryCache`/預設
Session 完全合理,**不要**看到 in-memory cache 就無腦建議換 Redis——只有在專案有跨機
共享狀態需求(多實例部署、掛 HAProxy 負載平衡、需要服務不中斷)時才建議導入。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=72362143
