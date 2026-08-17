# CotaUtility.PermProvider

## 何時適用

需要查詢員工在專案內角色/權限的後台系統,目的是共用 PermMgr 的權限資料,避免每個系統
自己維護一份權限表。支援 .NET Framework 4.6.1+ 及 .NET Core 2.0+。內部透過
`IDistributedCache`(可搭配 Redis)快取,預設 30 分鐘過期,並支援 Webhook 通知即時清快取。

## 偵測特徵

- 專案自己有一張「員工-角色」或「員工-權限」對照表,並自己寫查詢/判斷邏輯
- 自訂的 RBAC(角色權限控管)實作,跟其他系統各自維護、沒有互通

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.PermProvider"`
- ASP.NET Core:`services.AddPermProvider()` + `app.UsePermWebhook()`
- .NET Framework:`new PermClient(new PermOptions { ProjectName = "..." })`

## 已用時的正確用法檢查清單

- [ ] ASP.NET Core 專案是否有註冊 `app.UsePermWebhook()`,讓權限異動能即時清快取
      (沒註冊的話權限變更要等 30 分鐘快取過期才生效)
- [ ] .NET Framework 專案是否有在 `PermOptions` 明確填 `ProjectName`(文件提到
      .NET Framework 可能抓不到專案名稱,需要手動指定)
- [ ] .NET Framework 專案因無法用 Webhook,若有即時性需求,是否已自行實作清快取端點

## 未用時的替換建議

```csharp
// Program.cs
builder.Services.AddPermProvider();
app.UsePermWebhook();

// 使用
public class MyController(PermClient permClient) : Controller
{
    public async Task<IActionResult> Index()
    {
        bool canEdit = await permClient.HasPermissionAsync("033815", "ASSIGN_MGR");
        List<string> editors = await permClient.GetEmployeesByPermissionAsync("ASSIGN_MGR");
        return View();
    }
}
```

其餘方法:`HasRoleAsync` / `GetPermissionCodesAsync` / `GetRoleCodesAsync` /
`GetEmployeesByRoleAsync`。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=133792504
