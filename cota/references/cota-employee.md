# CotaEmployee 員工資訊

## 何時適用

需要查詢員工基本資料(姓名、員存帳號、職稱、所屬單位、在職狀態)、員工權限等級
(分行/部門/櫃員/業務別)的專案。資料來源:Cotashare、svremp。
命名空間 `CotaUtility.Models`,支援 .NET Framework 4.8 與 .NET Core。

**注意**:此模組出自舊版單體 `CotaUtility`(2023.12.01 EOS)時期的文件,是否已拆成
獨立維護的套件待確認——建議新專案使用前先查 CotaNuGet 來源裡有沒有對應的獨立
套件,不要直接裝已 EOS 的單體 `CotaUtility`。

## 偵測特徵

- 自己維護員工資料表(員編、姓名、員存帳號、單位、職稱)並自己寫查詢
- 自己刻的員工權限等級查詢(分行碼/部門碼/櫃員碼/業務別/權限等級)
- 從 AD 抓員工屬性當員工資料用(AD 沒有員存帳號、權限等級這些銀行內部欄位)

## 是否已用 CotaUtility

- 程式碼有 `using CotaUtility.Models;` + `EmployeeModel` / `AuthorityLevelModel`
- `.csproj` 有對應的 PackageReference(套件名待確認,見上方注意)

## 主要 API(皆為靜態方法)

| 類別 | 方法 | 說明 |
|---|---|---|
| `EmployeeModel` | `GetByEmpNo(string empNo)` | 透過員編取得員工資料 |
| `AuthorityLevelModel` | `GetByEmpNo(string empNo)` | 透過員編取得 svremp 中員工權限等級清單 |
| `EmpCardModel` | `GetByCryptUtil(string hiseed, string hisignedhash)` | 驗證入口網簽章並取得員工晶片卡資訊(失敗拋 Exception) |
| `DepartmentModel` | — | 單位資訊(員工資料內嵌) |
| `RankModel` | — | 職稱資訊(員工資料內嵌) |

`EmpCardModel` 欄位:`EmpNo`、`EmpName`、`LoadTime`(上個網頁 load 時間)、`CardNo`
(晶片卡卡號)、`CardReaderNo`(讀卡機序號)、`LoginTime`(入口網登入時間)、
`CardSerialNo`(晶片卡製卡序號)。使用前提:先註冊相關 COM 元件及匯入相關機碼
(見 Confluence 頁)。這跟 `references/network.md` 的 hiseed 驗證是同一套機制的
封裝版——需要「驗證簽章 + 拿晶片卡資料」時用這個,只需要驗證時用 network.md 的
手刻流程。

另有 `DateTimeConverter`(命名空間 `CotaUtility`,日期時間格式轉換)與
`DateDivider`(日期分隔線類型)兩個小工具模組,同屬舊版單體時期文件。

`EmployeeModel` 欄位:`EmpNo`(員編)、`Name`(姓名)、`Id`(統一編號)、`Account`
(員存帳號)、`Work`(擔任工作代號)、`HasLicense`(證照)、`Level`(職等)、`Rank`
(RankModel)、`Department` / `DisPatchDepartment`(DepartmentModel,所屬/派駐單位)、
`IsManager`(是否幹部)、`IsDirector`(是否單位主管)、`Status`(在職狀態)、
`ArrivedDate` / `LeavedDate`、`AuthorityLevels`(AuthorityLevelModel[])。

`DepartmentModel` 欄位:`PersonnelCode`(人事單位代碼)、`DpCode`(營業單位代碼)、
`Name`、`IsActive`、`Type`(0=總行部門,1=分行部門)。

`RankModel` 欄位:`RankCode`、`Name`(簡稱)、`FullName`、`IsActive`。

`AuthorityLevelModel` 欄位:`BrSn`(分行碼)、`DpSn`(部門碼)、`TellerCode`(櫃員碼)、
`BusinessType`(業務別)、`Level`(權限等級)。

## 與 PermProvider 的區分

PermProvider 查的是「專案內角色/權限」(PermMgr 維護的應用層權限);CotaEmployee
查的是「員工本身的人事資料與 svremp 權限等級」。兩者解決不同問題,可能同時使用,
不要互相替代。

## 參考

- CotaEmployee 員工資訊: https://svrconf.cotabank.com/pages/viewpage.action?pageId=65700211
- EmployeeModel 員工模組: https://svrconf.cotabank.com/pages/viewpage.action?pageId=65700263
- AuthorityLevelModel 員工權限等級模組: https://svrconf.cotabank.com/pages/viewpage.action?pageId=65700278
- DepartmentModel 單位資訊模組: https://svrconf.cotabank.com/pages/viewpage.action?pageId=65700249
- RankModel 職稱模組: https://svrconf.cotabank.com/pages/viewpage.action?pageId=65700257
