# CotaUtility.PermProvider

> 本 reference 依 Confluence「CotaUtility.PermProvider 後臺權限管理系統 Client 套件」第 9 版（2026-08-28）及本次權限管理系統公告整理；公告中的套件版本為 1.0.5。

## 何時適用

需要查詢員工在專案內角色/權限的後台系統,目的是共用 PermMgr 的權限資料,避免每個系統
自己維護一份權限表。支援 .NET Framework 4.6.1+ 及 .NET Core 2.0+。權限管理系統的
專案異動、指派規則與人員異動通知也屬於串接時要核對的後台控制鏈；Client 本身主要負責
查詢資料。內部透過 `IDistributedCache`(可搭配 Redis)快取,預設 30 分鐘過期,並支援
Webhook 通知即時清快取。

## 權限管理系統公告

### 後台流程與指派規則

- 專案異動流程現在只需要「設計組長」核可,不再需要「管理組長」核可。既有串接若仍把
  「管理組長」當成必經核可者,要重新核對流程設定與畫面提示。
- 新增法遵主管指派規則。
- 指派規則可排除特定單位,例如「所有單位,但不包含 XX 部」；設定或驗收規則時要確認
  排除條件確實生效,不要只驗證「所有單位」的正向結果。

### 人員異動通知

- 角色指派給特定人員時,該人員調離單位或離職,通知指派人員。
- 專案成員指派給特定人員時,該人員調離單位或離職,通知專案管理人。

上述五項是權限管理系統的後台流程、指派與通知行為,不是由 `PermClient` 另外實作的查詢
方法。串接驗收時應把核可對象、法遵主管規則、單位排除條件與通知收件人列入和 PermMgr
設定的對帳範圍。

## 套件 1.0.5 更新

### 同步方法

因 .NET Framework 呼叫非同步方法可能發生卡住,1.0.5 新增與既有非同步方法對應的同步
查詢方法。遇到同步內容、舊版 ASP.NET 或 UI `SynchronizationContext` 需要同步呼叫時,
使用同步方法,不要用 `.Result` 或 `.Wait()` 自己把非同步工作包住。

同步方法包括:

- `GetRoles(empNo)` / `GetRoleCodes(empNo)` / `HasRole(empNo, roleCode)`
- `GetPermissions(empNo)` / `GetPermissionCodes(empNo)` /
  `HasPermission(empNo, permissionCode)`
- `GetEmployeesByRole(roleCode)` / `GetEmployeesByPermission(permissionCode)`
- 帶過濾條件的 `GetEmployeesByRole(roleCode, filter)` /
  `GetEmployeesByPermission(permissionCode, filter)`

高併發 Web 路徑或需要維持 UI 響應時仍使用 `Async` 版本；同步方法只是避免典型
sync-over-async deadlock,仍會同步等待遠端服務回應。

### 反查人員清單的單位過濾

反查角色或權限的人員清單時,可帶入 `PermFilter`:

```csharp
List<string> departmentAdmins = client.GetEmployeesByRole(
    "SYSTEM_ADMIN", new PermFilter { DpCode = "0008" });

List<string> branchEditors = await client.GetEmployeesByPermissionAsync(
    "ASSIGN_MGR", new PermFilter { Branch = "0008" });
```

- `PermFilter.DpCode` 與 `PermFilter.Branch` 是不同的單位代碼,可單獨使用。
- 兩者同時指定時採 `AND` 條件。
- 套件會使用 API 回傳並快取的員工單位資料,在 NuGet 元件內以不分大小寫方式過濾。
- `Branch` 使用員工目前有效的單位代碼；`OtherBr` 有值時優先,否則使用
  `Employee.Branch`。

## 偵測特徵

- 專案自己有一張「員工-角色」或「員工-權限」對照表,並自己寫查詢/判斷邏輯
- 自訂的 RBAC(角色權限控管)實作,跟其他系統各自維護、沒有互通

## 是否已用 CotaUtility

- `.csproj` 有 `<PackageReference Include="CotaUtility.PermProvider">`
- ASP.NET Core:`services.AddPermProvider()` + `app.UsePermWebhook()`
- .NET Framework:`new PermClient()` 或 `new PermClient(new PermOptions { ... })`

## 已用時的正確用法檢查清單

- [ ] ASP.NET Core 專案是否有註冊 `app.UsePermWebhook()`,讓權限異動能即時清快取
      (沒註冊的話權限變更要等 30 分鐘快取過期才生效)
- [ ] .NET Framework 專案若自動偵測專案名稱失敗,是否在 `PermOptions` 填入
      `ProjectName` 作為備援(不需要無條件手動填寫)
- [ ] .NET Framework 專案因無法用 Webhook,若有即時性需求,是否已自行實作清快取端點
- [ ] .NET Framework 若曾以 `.Result` 或 `.Wait()` 呼叫非同步方法,是否改用 1.0.5
      對應的同步方法,並依流量情境保留適當的 `Async` 使用方式
- [ ] 反查角色/權限的人員清單若有單位範圍,是否使用 `PermFilter.DpCode` 或
      `PermFilter.Branch`,並確認兩者同時指定時的 `AND` 語義
- [ ] 若專案參與 PermMgr 的流程或指派設定,是否已對帳設計組長核可、法遵主管指派、
      特定單位排除,以及角色/專案成員異動通知的收件人

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
        List<string> departmentEditors = await permClient.GetEmployeesByPermissionAsync(
            "ASSIGN_MGR", new PermFilter { DpCode = "0008" });
        return View();
    }
}
```

## .NET Framework 同步用法

```csharp
using (var client = new PermClient())
{
    bool canEdit = client.HasPermission("033815", "ASSIGN_MGR");
    List<string> editors = client.GetEmployeesByPermission(
        "ASSIGN_MGR", new PermFilter { Branch = "0008" });
}
```

其餘方法:

- 角色:`GetRoles` / `GetRolesAsync` / `GetRoleCodes` / `GetRoleCodesAsync` /
  `HasRole` / `HasRoleAsync`
- 權限:`GetPermissions` / `GetPermissionsAsync` / `GetPermissionCodes` /
  `GetPermissionCodesAsync` / `HasPermission` / `HasPermissionAsync`
- 反查:`GetEmployeesByRole` / `GetEmployeesByRoleAsync` /
  `GetEmployeesByPermission` / `GetEmployeesByPermissionAsync`
- 反查方法的 `Async` 與同步版本都支援選填的 `PermFilter` overload。

## 參考

https://svrconf.cotabank.com/pages/viewpage.action?pageId=133792504
