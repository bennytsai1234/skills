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

- [ ] **新申請專案是否使用當下最新版 Redis 連線程式碼／CotaRedis 套件**，並以申請帳號的執行身分連線（2026-10-01 使用者確認）。下方 v1.1.0 / v1.2.x 是已驗證的歷史機制，不把 v1.2.x 當成固定的最新版。
- [ ] 套件版本是否跟 Redis 帳號的建立方式相符(見下方「帳號與版本」)。帳號是用新方式(AD User)
      建的專案需要新版驗證機制，停在 v1.1.0 會在所有節點 `WRONGPASS`
- [ ] 是否用新式的 `environment: RedisEnvironment.Internal/Dmz/BrSys` 參數,而不是舊式
      `isExternalProject: bool`(舊寫法仍可用但文件標示建議遷移到新版)
- [ ] `AddCotaRedisSession` 是否確實**取代**掉原本的
      `AddDistributedMemoryCache()`/`AddDataProtection().PersistKeysToFileSystem(...)`(這兩行應該被註解掉或移除,不是並存)
- [ ] 若有用 `ICotaRedisPubSub`,是否額外呼叫了 `AddCotaRedisPubSub()`(光注入
      Cache/Session 不會自動附帶 PubSub 服務)
- [ ] 遇到 `RedisTimeoutException` 時,是否已核對過 exception 訊息裡的 `clientName`
      跟系統組申請的 Redis 帳號資訊是否一致(這是文件列出的常見問題)

## 連線參數從哪裡來(不用寫連線字串)

**專案端不設定 Redis 位址,也不寫帳密**,全部走套件內建預設值——`appsettings.json`
裡看不到 Redis 區段是正常的,不是漏設定。實際呼叫通常只帶跟專案有關的參數:

```csharp
builder.Services.AddCotaRedisSession(options =>
{
    options.Cookie.Name = ".<專案>.Session";   // 同主機多專案要具名,避免互相覆蓋
});
```

`CotaRedisCacheOptions` 的預設值(v1.1.0 起;v1.2.x 依 `RedisEnvironment` 決定主機群):

| 屬性 | 預設 |
|---|---|
| `HostAndPorts` | Internal:`svrRD1～3.cotabank.com` 的 `64{InstanceId}`／`74{InstanceId}` 共 6 個節點(Redis 6 cluster;svrRd1 = 192.168.251.120、svrRd2 = .121);Dmz 為 `svrRDn.dmz.cotabank.com`、BrSys 為 `svrRDn.br.cotabank.com` |
| `InstanceId` | 2 |
| `IsExternalProject` | false(對外專案才改,新式寫法用 `RedisEnvironment`) |

程式不需要也不應該寫帳密,但**系統組必須先在 Redis 上開好對應的使用者**,否則連線會被拒。
帳密怎麼產生取決於套件版本,見下一節。

## 帳號與版本(v1.1.0 → v1.2.x 的驗證方式不同)

套件 nuspec 的版本說明(Confluence 頁面沒有寫到這點):

> v1.2.0 修改驗證方式,Redis帳號改用 AD User(原本為專案名稱)
> v1.2.2 新增支援分行系統的Redis,更新至此版本後注意要請系統組變更密碼

| 版本 | 帳號 | 密碼 |
|---|---|---|
| v1.1.0 | 組件名稱(空白→`_`、`:`→`.`)轉大寫,即 `Helper.GetCotaRedisUserName()` | 帳號字串的 SHA256(小寫 hex) |
| v1.2.x | **執行身分的 AD User** 轉大寫(由原生 `CotaRedisCodeGetter.dll` 取得) | `CotaRedisCodeGetter.dll` 產生 |

v1.2.x 的登入順序(反編譯 1.2.4 確認):

1. 先用「執行身分 + CodeGetter 密碼」試登。
2. 試登回的是**驗證失敗**(WRONGPASS)才退回 v1.1.0 的組件名稱公式;若是逾時等**非驗證錯誤**,
   套件會直接沿用新帳密,不會退回。

實務上的後果(已在 IIS App Pool 內實測):

- **執行身分決定帳號**。IIS 上是 App Pool 身分(AP User,例如 `COTABANK\BoardMonitor` →
  `BOARDMONITOR`;`ApplicationPoolIdentity` 則取 pool 名稱)。AP User 通常依專案命名,
  所以帳號看起來仍像「專案名大寫」,但來源已經不是組件名稱。
- **新方式建立的帳號,舊公式登不進去**:同一個 App Pool 內,新方式 6 個節點 OK、組件名稱公式
  6 個節點都 `WRONGPASS`。這類專案一定要 v1.2.x,且必須以 AP User 身分執行。
- **舊方式建立的帳號**(例如仍用 v1.1.0 的既有專案)升到 v1.2.x 後,新方式會 WRONGPASS,靠
  fallback 才連得上;要徹底改用新方式,依 v1.2.2 說明請系統組變更密碼。
- 分辨帳號屬於哪一種:在**同一個 App Pool 身分**下分別只用新方式、只用組件名稱公式登入,
  看哪個成功。
- 套件預設沒有 logger,不會記錄實際走哪條路徑;可從 `RedisCacheOptions.ConfigurationOptions.User`
  讀出實際登入的帳號並自行記錄。套件的 key 前綴也是「實際登入帳號 + `:`」,專案自己的 key
  namespace 應以這個值為準,不要自行用組件名稱推算。

連不上 Redis 會在**啟動階段**就讓站台掛掉,所以新機器/新環境第一次部署時,Redis 使用者
有沒有開通是站台起不來的常見原因之一。本機連得到 `svrRd1` 不代表部署主機的網段也連得到。

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

注意:專案有使用 `AddCotaRedisSession` 時會**一併設定 CotaRedisCache**,不需要再
另外呼叫 `AddCotaRedisCache`。

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
`clientName` 跟系統組核對申請資訊(v1.2.x 的 `clientName` 是實際登入的帳號,可能是 AD User
也可能是 fallback 的組件名稱)。直接對單一節點連線可看到真正原因:`WRONGPASS invalid
username-password pair` 代表帳號不存在、未啟用或密碼不符,Redis 不會區分這三種。

**不要用開發者身分的 console 探測程式判斷帳號好壞**:v1.2.x 會以開發者自己的 AD 帳號登入
(一定失敗),再退回組件名稱公式(新方式建的帳號也會失敗),結論會是「帳號壞了」,但其實
只是身分不對。要在 AP User 的 App Pool 內驗證;同一個 pool 內 ASP.NET Core 不能混用
in-process／out-of-process,也不能放兩個 in-process app,暫時的探測 app 要成為該 worker
第一個載入的 app(stop/start pool 後先打探測 app,測完再 stop/start)。要確認測試環境真的有連上 Redis,可在命令提示字元執行
`netstat -ano | find "251.12"`(依實際 Redis Server IP 網段調整關鍵字),看有沒有
`ESTABLISHED` 狀態的連線。

## 前置作業(套用前必須做)

1. **使用的主機上要安裝 Microsoft Visual C++ Redistributable**(文件列明的前置條件,
   部署機/開發機都要有;v1.2.x 的原生 `CotaRedisCodeGetter.dll` 需要它)。
2. 需要先在 Tracko 專案上線申請單跟系統組申請 Redis Server 使用者(帳號=專案名稱轉大寫,
不能有冒號;需指定專案區域:內部/DMZ/核心系統)。v1.2.x 實際登入的是執行身分的 AD User,
申請時要確認帳號對應的是專案的 AP User。這不是程式碼層面能自己解決的,回報時
要提醒使用者這個前置作業。

**依申請狀態分流**（2026-10-01 使用者確認）：

- **尚未申請或資源未到位**：先用本機 Redis 開發，保留 AA + Redis 目標；不要讓尚未開通的公司帳號阻塞本機功能。
- **已申請且資源到位**：使用申請帳號連公司 Redis。新申請專案必須用當下最新版連線程式碼／CotaRedis 套件，舊版組件名稱公式不能用來驗證新帳號。
- **使用公司 CotaRedis 連線路徑時**：套件依 `RedisEnvironment.Internal/Dmz/BrSys` 指向公司 Redis，不會因為在開發機執行就自動切換 localhost。先前核對的版本沒有本機 fallback；不要把這個限制誤寫成「申請前不能先用本機 Redis 開發」。

公司 Redis 帳號跟著執行身分走。開發機以未獲授權的開發者身分跑，登入失敗不能證明申請帳號有問題；在本機 IIS 測公司連線時，用申請的 AP User 身分執行並驗證。

## 適用情境提醒(專案沒有這個功能時怎麼判斷要不要建議)

如果專案本來就是單機部署、沒有多實例/HA 需求,維持 `AddDistributedMemoryCache`/預設
Session 完全合理,**不要**看到 in-memory cache 就無腦建議換 Redis——只有在專案有跨機
共享狀態需求(多實例部署、掛 HAProxy 負載平衡、需要服務不中斷)時才建議導入。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=72362143
