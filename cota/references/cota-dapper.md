# CotaUtility.CotaDapper

**注意**:Confluence 文件本身標示「(未完成)」。建議此模組前,先跟開發團隊確認目前是否
已穩定可用、有沒有更新的文件,不要當作已定案的規範直接套用。

## 何時適用

Dapper 風格存取 MSSQL,且專案採 Repository + DI 模式(而非 CotaDB 的 static/直接 new
風格)。目標 .NET Standard 2.1,**僅支援 .NET Core**。

## 偵測特徵

- 專案已經在用 Dapper(`Dapper` NuGet 套件)但連線管理是自己手刻的
  (自己包一層 `IDbConnection` factory)
- Repository/Service 建構式注入自訂的 DB 連線包裝介面,內部用原生 `SqlConnection` +
  Dapper 擴充方法(`QueryAsync`/`ExecuteAsync` 等)

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.CotaDapper"`
- 程式碼建構式注入 `ICotaDapper`

## 已用時的正確用法檢查清單

- [ ] 連線是否透過 `SetConnection(dbName)` 或
      `SetConnection(dataSource, settings, dbName)` 設定,而不是散落在各處硬編碼連線字串
- [ ] 是否有依賴 `Dispose` 自動關連線來偷懶——文件特別提醒這只是「保險」,開發者仍應
      養成主動呼叫 `Close()` 的習慣,長時間持有連線不關會佔用連線池

## 未用時的替換建議

```csharp
// Program.cs / Startup.cs 加入服務
using CotaUtility.CotaDapper;
builder.Services.AddCotaDapper(); // 或 AddCotaDapper("CotaShare") 直接帶預設資料庫

// Repository
public class TestRepository : ITestRepository
{
    private readonly ICotaDapper _dapper;
    public TestRepository(ICotaDapper dapper)
    {
        _dapper = dapper;
        _dapper.SetConnection("CotaShare");
    }
}
```

## 方法總覽

連線管理:`SetConnection(dbName)` / `SetConnection(dataSource, Dictionary<string,string> settings, dbName)` /
`Open()` / `Close()`(關閉並釋放連線資源)/ `GetConnectionState()` / `ChangeDB(dbName)` /
`StartTransaction()` / `Commit()` / `Rollback()`。

查詢/執行(每個都有同步 + `Async` 版本,參數固定為 `(string sqlString, object parameters, int? timeout, CommandType type)`):
`ExecuteScalar<T>`(純量查詢)、`QuerySingle<T>`(單筆,查無或多筆會丟例外)、
`QuerySingleOrDefault<T>`、`QueryFirst<T>`(首筆)、`QueryFirstOrDefault<T>`、
`Query<T>`(多筆)、`Execute`(非查詢命令)、`QueryMultiple`(多組命令)、
`ExecuteReader`、`GetDataTable`。

`GetConnectionState()` 回傳 `ConnectionState` 列舉:`Closed`(0)/`Open`(1)/
`Connecting`(2)/`Executing`(4)/`Fetching`(8)/`Broken`(16)。

## 跟 CotaDB 的選用判斷

見 `references/cota-db.md` 的對應段落。簡單說:原生 ADO.NET 手感、跨 Framework/Core 用
CotaDB;Dapper + DI 手感、且確定專案只跑 .NET Core、且已確認 CotaDapper 目前可用,才選
這個。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=102236505
