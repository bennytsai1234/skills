# CotaUtility.SecureMySql

## 何時適用

**分行系統(分行系統業務,非 Br 前綴的中台架構專案)** 存取 MySQL 資料庫。這是目前
CotaUtility 系列裡最新的模組,強調不讓應用程式碰到明碼 MySQL 帳密。

支援:.NET 5/6/7/8,Windows x64/x86,底層驅動 MySqlConnector,可選搭配 Dapper 或直接
用 ADO.NET。

## 偵測特徵

- 直接使用 `MySqlConnector` 或 `MySql.Data` 套件的 `MySqlConnection`
- 連線字串內含明碼密碼(`Password=...` 出現在程式碼或設定檔)
- 手刻的 MySQL 帳密管理/憑證讀取邏輯

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.SecureMySql"`
- 程式碼注入 `ISecureMySqlConnectionFactory`

## 已用時的正確用法檢查清單

- [ ] **一律使用參數化 SQL**,不可字串拼接使用者輸入(套件文件明確警告這點,是最容易
      犯的錯):
      ```csharp
      // ❌ 絕對不要
      command.CommandText = "SELECT * FROM Users WHERE Name = '" + userName + "'";
      ```
- [ ] 沒有嘗試取用或記錄 `ISecureMySqlConnection.ConnectionString`——套件設計上這個屬性
      永遠回傳遮蔽值,不可設定,若程式碼試圖解析/還原真實連線字串就是誤用
- [ ] MySQL 帳號權限是否已對應到「執行程式的 Windows 使用者」——套件依目前 Windows
      User 取得憑證,執行應用程式或 Windows Service 的帳號必須具備對應 MySQL 權限

## 未用時的替換建議

```csharp
// Program.cs
using CotaUtility.SecureMySql.DependencyInjection;
using CotaUtility.SecureMySql.Options;

builder.Services.AddSecureMySql(options =>
{
    options.DefaultEndpoint = new MySqlEndpoint
    {
        Server = "SvrDBCN.core.cotabank.com",
        Port = 3306,
        Database = "application_db",
    };
    options.RedisEnvironment = RedisEnvironment.BrSys; // 依專案區域選擇
});

// Repository
public sealed class UserRepository(ISecureMySqlConnectionFactory connectionFactory)
{
    public async Task<IReadOnlyList<User>> GetActiveUsersAsync(CancellationToken ct)
    {
        await using var connection = await connectionFactory.CreateAsync(ct);
        return (await connection.QueryAsync<User>(
            new CommandDefinition("SELECT Id, Name FROM Users WHERE IsActive = @IsActive",
                new { IsActive = true }, cancellationToken: ct))).AsList();
    }
}
```

不需要也無法取得實際 MySQL 密碼、完整連線字串或內層 `MySqlConnection`,套件也不會在
Exception/Log 輸出這些資訊。

## 進階設定

```csharp
builder.Services.AddSecureMySql(options =>
{
    options.DefaultEndpoint = new MySqlEndpoint { Server = "...", Port = 3306, Database = "..." };
    options.RedisEnvironment = RedisEnvironment.Internal; // Internal / Dmz / BrSys
    options.MinimumPoolSize = 5;
    options.ConnectionLifetimeSeconds = 20 * 60 * 60;
});
```

Transaction 用法:

```csharp
await using var connection = await connectionFactory.CreateAsync(ct);
using var transaction = connection.BeginTransaction();
await connection.ExecuteAsync(new CommandDefinition(
    "UPDATE Users SET IsActive = @IsActive WHERE Id = @Id",
    new { Id = userId, IsActive = false }, transaction, cancellationToken: ct));
transaction.Commit();
```

若同一個應用程式要存取多個 MySQL Database,兩種做法:

**A. 建立連線時指定 endpoint**(該次連線只用指定的 endpoint,不修改 DefaultEndpoint):

```csharp
var endpoint = new MySqlEndpoint { Server = "reporting-mysql...", Port = 3306, Database = "reporting_db" };
await using var connection = await connectionFactory.CreateAsync(endpoint, ct);
```

**B. Named Endpoint**(同一個應用程式要連兩個不同 MySQL Server 時,兩個 endpoint
都用名稱註冊、不設 DefaultEndpoint):

```csharp
builder.Services.AddSecureMySql(options =>
{
    options.RedisEnvironment = RedisEnvironment.Internal;
})
.AddSecureMySqlEndpoint("CI", new MySqlEndpoint
{
    Server = "SvrDbCI.core.cotabank.com",
})
.AddSecureMySqlEndpoint("CN", new MySqlEndpoint
{
    Server = "SvrDbCN.core.cotabank.com",
});

// 建立連線時指定名稱
await using var connection = await connectionFactory.CreateAsync("CI", ct);
```

Named Endpoint 注意事項:

- `CreateAsync()` 無參數用法只適用於已設定 `DefaultEndpoint` 的情境。
- `AddSecureMySqlEndpoint` 的名稱不可重複(大小寫不敏感)。
- 跨 database 查詢(如 `DBA.ATable` 與 `DBB.BTable`)時,兩個 database 必須位於
  **同一個 MySQL Server**,且目前 Windows 使用者必須具備相應權限。

支援範圍:.NET 5/6/7/8、Windows x64/x86、MySQL Driver 為 MySqlConnector、Data Access
用 ADO.NET(Dapper 為選用,套件本身不相依 Dapper)。

## 適用情境提醒

這是「分行系統」場景專用(對照分行系統的 MySQL 存取需求),如果專案不是分行系統相關、
或資料庫是 MSSQL,不適用此模組,改看 `references/cota-db.md` /
`references/cota-dapper.md`。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=133792616
