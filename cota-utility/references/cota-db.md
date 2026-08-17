# CotaUtility.CotaDB

## 何時適用

原生 ADO.NET 風格(不透過 Dapper/EF,直接下 SQL 字串)存取 **MSSQL** 資料庫的專案。
Target netstandard2.0,.NET Framework 跟 .NET Core 專案都能用。上線日 2023.11.28。

v1.0.3 新增:備用資料來源(Failover Partner,支援 AlwaysOn 容錯移轉)、連線池使用率
分級設定、連線生命週期統一設為 30 秒(避免拿到過期連線)。附有 GitHub Copilot 指引檔
(`CotaUtiity.CotaDB.usage.instructions.md`),可用來輔助升級到 1.0.3。

## 偵測特徵(專案裡有沒有在做這件事)

- `new SqlConnection(` / `SqlCommand`
- 手動 `.Open()` / `.Close()` 搭配 `ExecuteReader` / `ExecuteNonQuery` / `ExecuteScalar`
- 手刻的 Transaction 管理(`BeginTransaction()` / `Commit()` / `Rollback()`)
- 手刻的 `DataSet`/`DataTable` fill 邏輯(`SqlDataAdapter.Fill`)

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.CotaDB"`
- 程式碼有 `using CotaUtility;` + `new CotaDB(...)`
- **注意舊版陷阱**:如果 `.csproj` 只有 `<PackageReference Include="CotaUtility"` (沒有
  `.CotaDB` 後綴),代表還在用 2023.12.01 已 EOS 的單體套件,算「用錯」,應遷移到拆分
  後的 `CotaUtility.CotaDB`。

## 已用時的正確用法檢查清單

- [ ] `SqlParameter` 是否明確指定 `SqlDbType`(例如
      `new SqlParameter { ParameterName = "@id", SqlDbType = SqlDbType.Int, SqlValue = 1 }`)。
      沒指定型別會讓 SQL Server 自行推斷,可能拖慢效能、甚至型別誤判(例如把整數推斷成
      NVarChar)。
- [ ] Transaction 是否透過 `Transaction(Func<CotaDB,bool>)` 或泛型版本
      `Transaction<T>(Func<T,bool>)` callback 執行,而不是自己手動開關連線、分散在多處
      呼叫 `StartTransaction`/`Commit`/`Rollback`。
- [ ] 版本是否 1.0.3+(AlwaysOn 容錯移轉 + 連線池調校);較舊版本可提醒升級,非必要,
      視專案是否有 AlwaysOn 需求而定。

## 三種建構子

| 建構子 | 用途 | 連線字串組成 |
|---|---|---|
| `CotaDB(string dbName)` | 只給資料庫名稱,其餘固定 | 來源固定 `svrdb`,固定
  `persist security info=True;Integrated Security=SSPI;packet size=4096;TrustServerCertificate=true;Column Encryption Setting=enabled;database={dbName}` |
| `CotaDB(string dataSource, string settings, string dbName)` | 自訂來源、連線參數、資料庫名稱 | `data source={dataSource};{settings}database={dbName}` |
| `CotaDB(SqlConnection sqlConnection)` | 共用既有的 SqlConnection(Transaction 場景用這個) | 沿用傳入的連線 |

`sqlConnectionString` 屬性可取得組好的連線字串,需要自行另外建立連線時可用。

## 未用時的替換建議

```csharp
// 手刻版
using (var conn = new SqlConnection(connStr))
{
    conn.Open();
    using var cmd = new SqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("@BiSn", "55");
    var rows = cmd.ExecuteNonQuery();
}

// CotaDB 版
CotaDB cotaDB = new CotaDB("dp"); // 資料庫名稱,連線資訊固定為 svrdb + SSPI 整合驗證
var sqlParameters = new List<SqlParameter> {
    new SqlParameter { ParameterName = "@BiSn", SqlDbType = SqlDbType.VarChar, SqlValue = "55" }
};
int rows = cotaDB.ExecuteNonQuery(
    "INSERT INTO dp.dbo.BrInfo (BiSn, BiName) VALUES (@BiSn, 'TEST')",
    sqlParameters, timeout: 5);
```

常用方法:`ExecuteNonQuery` / `ExecuteScalar` / `GetDataSet`(多語句查詢)/
`GetDataTable`(單語句查詢)/ `ChangeDatabase` / `State()`(需搭配
`CotaDB(SqlConnection)` 建構式)/ `StartTransaction`+`Commit`+`Rollback`+`CloseDB`
(後三者也都需搭配 `CotaDB(SqlConnection)` 建構式使用)。

`Transaction`/`Transaction<T>` 用法:callback 收到的參數(通常命名為 `db`)是套件用同一個
`SqlConnection` 另外 new 出來的 `CotaDB` 物件,**要用這個 callback 參數執行
StartTransaction/Commit/Rollback,不是原本外層的 cotaDB 變數**——這是文件特別強調、
容易寫錯的地方:

```csharp
CotaDB cotaDB = new CotaDB("dp");
bool result = cotaDB.Transaction((db) => {
    try
    {
        db.StartTransaction();          // 用 callback 參數 db,不是外層的 cotaDB
        db.ExecuteNonQuery(sql1, ps1);
        db.ExecuteNonQuery(sql2, ps2);
        db.Commit();
        return true;
    }
    catch (Exception)
    {
        db.Rollback();
        return false;
    }
});
```

泛型版本 `Transaction<T>(Func<T,bool>) where T : CotaDB` 可以讓 callback 參數是繼承
`CotaDB` 的自訂 Repository 類別(建構子要有 `CotaDB(SqlConnection)`),同一個 Transaction
裡呼叫多個自訂的業務方法(而不是散裝 SQL 字串),寫法上更貼近 Repository 模式。

## SqlParameter 型別:為什麼要明確指定 SqlDbType

```csharp
// 寫法一(建議):明確指定型別
var p = new SqlParameter { ParameterName = "@id", SqlDbType = SqlDbType.Int, SqlValue = 1 };

// 寫法二(不建議):沒指定型別,SQL Server 要自行推斷,可能影響執行計畫效能;
// 且如果 SqlValue 不小心寫成字串 "1",寫法一因為型別已固定為 Int 會嘗試轉型,
// 寫法二則可能被推斷成 NVarChar,行為不可預期
var p2 = new SqlParameter { ParameterName = "@id", SqlValue = 1 };
```

## 跟 CotaDapper 的選用判斷

如果專案風格是 Repository + DI(而不是 static/直接 new),且限定 .NET Core-only,可以
考慮用 `references/cota-dapper.md` 描述的 CotaDapper——但該套件文件目前標示「未完成」,
採用前務必跟開發團隊確認現況,不要預設它已經穩定可用。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=94568996
