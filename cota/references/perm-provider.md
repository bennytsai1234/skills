# CotaUtility.PermProvider

> 本 reference 依 Confluence「CotaUtility.PermProvider 後臺權限管理系統 Client 套件」第 9 版（2026-08-28）及本次權限管理系統公告整理；公告中的套件版本為 1.0.5。
> 「後台：申請新增專案」一節另依 2026-09-18 實際操作 PermMgr 後台與實測 `PermClient` 行為補寫，非 Confluence 內容。

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

## 後台：申請新增專案

> 依 2026-09-18 實際操作 `https://prjpermmgr.cotabank.com/permmgr/` 的畫面整理。
> 後台導覽分成「專案異動」「指派異動」「API 結果測試」「專案成員管理」四塊，
> 新專案串接走「專案異動 → 申請新增專案」。**送出後要經組長核可才會正式建立專案**，
> 所以串接排程要把核可的等待時間算進去,不要假設填完就能查到權限。

申請是五個步驟的精靈,前一步沒填完後面會白填,依序是:基本資訊 → MEMBER_MGR
指派規則 → 自訂權限 → 自訂角色 → 送出確認。

### Step 1 基本資訊

| 欄位 | 必填 | 說明 |
|---|---|---|
| 專案代碼 | ✔ | **實際上要等於用戶端的「組件名稱」**,不是 `PermOptions.ProjectName` 填什麼就是什麼(見下方「ProjectName 只是備援」)。不一致的症狀是「所有人都查不到權限」,而且不會有錯誤 |
| 專案名稱 | ✔ | 顯示用 |
| 說明 | | |
| Webhook URL | | 權限異動時 PermMgr 會 POST 到這個網址通知清快取,對應程式端的 `app.UsePermWebhook()` |
| 指派核可模式 | | 決定專案內**角色指派**是否需經核可;選「立即生效」就不經核可 |
| 申請原因 | | 供審核人了解申請目的;**選「立即生效」時這欄不使用** |

Webhook URL 要填**對外看得到的完整網址**。程式裡 `UsePermWebhook()` 註冊的路徑是
`/perm/webhook`,但站台掛在 IIS 子應用程式底下時,那一層路徑是 PathBase、程式看不到,
對外網址要自己補上去——例如子應用程式 `/AISTT` 的站台要填
`https://<主機>/AISTT/perm/webhook`。不填的話權限改了要等套件的 30 分鐘快取過期才生效。

### Step 2 MEMBER_MGR 指派規則

設定**哪些人可以指派這個專案的專案成員**(指派管理人)。未設定時只有系統管理者能指派
此專案成員——也就是說這一步留空,之後每次加人都得找系統組。

- 指派方式:可選「指定員編」等規則;選指定員編時以員編或姓名搜尋後加入。
- 跨單位:開啟後,這組規則指派到的對象可以跨單位管理專案成員。
- 啟用日 / 結束日:規則的有效期間,預設帶出當日起算數年,到期後規則失效。

### Step 3 自訂權限

定義此專案的權限代碼,欄位是**權限代碼**(必填)、**權限名稱**(必填)、說明。
這裡的權限代碼就是程式端 `HasPermission(empNo, permissionCode)` 要傳的字串。

### Step 4 自訂角色

定義角色,每個角色有**角色代碼**(必填)、說明、**擁有權限**(勾選 Step 3 定義的權限)、
**可指派單位**(預設「未限制單位」,可改成指定單位)。權限要先在 Step 3 建好,
Step 4 才勾得到。

### Step 5 送出確認

列出這次送出的全部內容(基本資訊、MEMBER_MGR 指派規則、自訂權限、自訂角色)供最後核對。

### 串接時的對應關係

| 後台欄位 | 程式端 |
|---|---|
| 專案代碼 | **用戶端的組件名稱**(`AssemblyName`);`PermOptions.ProjectName` 只在自動偵測失敗時才用得到 |
| Webhook URL | `app.UsePermWebhook()` 註冊的 `/perm/webhook`,加上 PathBase |
| Step 3 權限代碼 | `HasPermission` / `HasPermissionAsync` 的第二個參數 |
| Step 4 角色代碼 | `HasRole` / `HasRoleAsync` 的第二個參數 |

### ⚠ ProjectName 只是備援,真正決定查哪個專案的是組件名稱

實測 1.0.5:`PermOptions.ProjectName` 的文件寫「預設自動偵測,偵測失敗時使用此值」,
字面就是它的行為——**偵測成功時,填進去的值完全不生效**。套件一律拿偵測到的組件名稱
去組 `GET {ServerUrl}/api/permissions/{專案}`。

所以 PermMgr 後台的「專案代碼」實際上綁在**用戶端的 `AssemblyName`** 上:

- 後台專案代碼要跟組件名稱一字不差,大小寫也要一樣。
- 改 `AssemblyName`、或把整個專案改名,權限會整組失效,而且不會有任何錯誤訊息。
- 寫探針或測試小程式驗證串接時,**探針的組件名稱也必須設成同一個值**,否則它查的是
  一個以探針自己命名的、不存在的專案,結果永遠是空的——這一點極容易把人帶偏,
  會讓人以為是後台沒指派好。

  ```xml
  <!-- 驗證用的 console 專案 -->
  <AssemblyName>你的專案代碼</AssemblyName>
  ```

`AddPermProvider(o => o.ProjectName = ...)` 仍然值得填,但要理解它是備援
(某些 host 模式下拿不到組件名),不是覆寫。

### ⚠ 查不到專案與沒有權限的回傳完全一樣

實測(2026-09-18):以一個**根本不存在的專案名稱**呼叫 `GetRoleCodes` / `GetPermissionCodes`
/ `HasPermission`,結果與「專案存在但該員工沒有任何權限」**一模一樣**——空清單、
`HasPermission` 回 false,不丟例外、不回錯誤碼。

所以下列四種情況在程式端看起來沒有差別:

1. 專案還沒送出申請
2. 申請送了但組長還沒核可
3. 專案代碼與 `ProjectName` 拼錯
4. 專案都好了,只是這個人沒被指派

串接驗收時**不能靠「程式沒報錯」判斷已經接通**,要用真的有被指派的帳號實際開一次
受保護的畫面。程式端把「查不到權限」當成「沒有權限」是對的(安全的失敗方向),
但要留一條 log 或一個可自行檢查的探針,否則現場只會回報「功能壞了」。

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
- [ ] 後台「專案代碼」與**用戶端的組件名稱**是否一字不差(不是 `PermOptions.ProjectName`
      填什麼就算什麼),Webhook URL 是否含 IIS 子應用程式的路徑前綴——這兩項填錯都不會
      報錯,只會表現成「所有人都沒權限」或「權限改了不生效」
- [ ] 是否已用真的有被指派的帳號實際開過受保護的畫面;查不到專案與沒有權限的回傳
      完全一樣,不能只靠程式沒報錯就當作接通

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
