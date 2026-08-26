# 版本控制與程式抄送流程(Git / Gogs)

公司 WEB 專案的版本控制與上線抄送流程。使用者問「怎麼建倉庫」「分支怎麼切」
「上線要怎麼抄送」「退版怎麼辦」時查這裡。

## 倉庫平台:Gogs

- 用 **AD 帳號**登入 Gogs 建倉庫;倉庫名 = 方案或專案名稱。
- 建完倉庫要**轉移所有權給組織**(倉庫設置 → 轉移倉庫所有權),各組代號:
  研發組 `Research`、數銀組 `DigitalBanking`、行內應用組 `WebForge`、
  外匯財會組 `FXAccounting`、台幣存匯組 `DpAtm`、授信信託組 `LoanTrust`。
- 權限由組長開。

## 分支與環境對應(重要)

| 分支 | 推送後效果 |
|---|---|
| `master` | 同步到**正式環境**的抄送目錄 |
| `dev`(注意大小寫) | 同步到**測試環境**的抄送目錄 |

- `master` 的版本紀錄**無法刪除**;退版用 `git revert` 再 push,不能用 reset。
- **不支援強制推送**(`git push --force`)。
- 建議:本機修改開新分支,要抄送時才合併到 `master`,讓 master 盡量乾淨、
  只放要上線的版本。
- 上線程式時**一定要看差異比對**。
- 抄送完畢後用 tag 記錄 online 版本:`git tag -a <tag>`;tag 不會隨 push 推送,
  要另外 `git push origin <tag>`。有 tag 記錄的話可用 GitPublishTool 小工具
  輔助抄送。
- 推送 master 後系統會同步一份到抄送系統目錄,但**要在抄送系統確認要抄送的
  檔案是最新的**再執行。

## 避免漏選檔案(抄送前檢查)

.NET Framework 專案常見漏選:DLL 元件忘了加入專案/忘記選、COM+ 元件忘記改設定、
只改了 B 檔忘了 A 檔的 Function、忘了 .csproj/web.config/web reference 檔。
.NET Core 專案常見漏選:NuGet 相關檔案少選、NuGet 偷偷更新版本異動到 dll 及
csproj。

**標準做法:先產出「有異動的檔案列表」再逐項檢查**——Git 用 GIT 檔案清單小工具
(選專案 + 選標籤即得清單);Source Safe 用 search + File Report。

## 原始碼檢測(Checkmarx SCA)

- 入口:`https://sca.cotabank.com/CotaSCA/`
- 壓縮原始碼送掃時,用 **7-Zip → 加入壓縮檔、格式選 zip**;舊的壓縮方式
  掃描時可能無法解壓縮導致失敗。

## 風險評估表與測試報告(異動單附件)

- **風險評估表**:抄程式的人填,送異動單時夾在程式異動管理系統的「相關附件」。
- **測試報告**:抄程式的人填上半部(至測試重點),傳給測試人員填下半部
  (測試項目起),完成後夾在異動單的「測試報告」。
- 範本:入口網 > 文件管理系統 > ISMS-3-003-T07;共用資料夾
  `\\192.168.253.237\0090\UserData\PublicData\第1B組專區\` 有範例。
- 快速產生風險評估報告的小工具:`http://192.168.251.169/cotareport/RiskScore`

## 緊急抄送

- 申請授權開放時間:**營業日 17:20 過後、非營業日**。
- 有統一的申請方式,COBOL / JAVA / WEB 各有處理流程(見參考頁)。

## 參考

- 專案設定GIT: https://svrconf.cotabank.com/pages/viewpage.action?pageId=64127149
- 【程式抄送】避免漏選檔案的方法: https://svrconf.cotabank.com/pages/viewpage.action?pageId=87360115
- 原始碼檢測: https://svrconf.cotabank.com/pages/viewpage.action?pageId=22282261
- 風險評估表與測試報告: https://svrconf.cotabank.com/pages/viewpage.action?pageId=35880970
- 緊急抄送相關說明: https://svrconf.cotabank.com/pages/viewpage.action?pageId=37683270
