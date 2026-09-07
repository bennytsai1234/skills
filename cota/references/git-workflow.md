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

## 原始碼檢測(Mend)

公司現行用 **Mend**,送件走內部入口;**舊的 Checkmarx `CotaSCA` 已停用**
(`https://sca.cotabank.com/CotaSCA/` 目前回 503)。

### 內部送掃入口

- 網址:`https://sca.cotabank.com/Mendsca`(頁面標題寫 **Mend SCA Scanner**,
  但實際跑的是 SAST,見下方警告)
- 驗證:**Windows 整合式驗證**(Negotiate/NTLM),用網域帳號直接進,不必另外登入。
  IIS 架設,匿名存取會回 401。
- 流程:選 **Application** → 選 **Project** → 上傳**原始碼 ZIP** → 送出掃描 →
  頁面顯示掃描佇列與即時輸出 → 「查詢掃描結果」或「前往 Mend 平台查詢結果」。
- Application 選項:`Demo`、`Dev`、`Prod`、`Restricted`、`Test_CICD`、`TMP`。
  (`Test_CICD` 的存在表示另有 CI/CD 串接路徑,細節待確認。)
- 上傳限制:**僅接受 `.zip`,上限 1.5 GB**。壓縮時用
  **7-Zip → 加入壓縮檔、格式選 zip**;舊 Checkmarx 時期就有「其他壓縮方式導致
  掃描端解不開而失敗」的紀錄,沿用同一個做法最保險。
- 到 Mend 平台查結果需要帳號,**該入口頁面上直接顯示可用的共用帳密**(附複製鈕),
  需要時到頁面上看,本 skill 不留存任何憑證。

### 送件實作細節(用腳本自動送掃時)

頁面是一般表單,底層就三個端點,可以直接用 Windows 整合式驗證呼叫:

| 端點 | 用途 |
|---|---|
| `POST {base}/Scan/Create` | 送件,`multipart/form-data` |
| `GET {base}/scan/stream/{jobId}` | 單一任務的即時輸出(**SSE,連線不會關**,腳本要設逾時或只取前幾筆) |
| `GET {base}/scan/queue/stream` | 掃描佇列的即時狀態(同為 SSE) |

`{base}` = `https://sca.cotabank.com/Mendsca`。`Scan/Create` 的欄位:

- `applicationName` —— Application 名稱字串(非 UUID)
- `projectName` —— Project 名稱字串
- `zipFile` —— 原始碼 zip

成功回 `{"success":true,"jobId":"<uuid>"}`,失敗回 `{"success":false,"error":"..."}`。

PowerShell 範例(不必處理帳密,走目前登入的網域身分):

```powershell
$form = @{ applicationName='Dev'; projectName='Dev_<專案>'; zipFile=Get-Item $zip }
Invoke-WebRequest -Uri "https://sca.cotabank.com/Mendsca/Scan/Create" `
  -Method Post -Form $form -UseDefaultCredentials -TimeoutSec 300
```

**Project 必須事先存在**——頁面的下拉沒有開啟 select2 的 tags/建立新項目,送一個不存在的
名稱不會幫你建。可用的 Project 清單直接內嵌在首頁 HTML 的 `window.__projectsByApp`
(以 Application 的 UUID 為 key),要查有沒有某專案,抓首頁解析這個物件即可,不必點 UI。

命名慣例(從既有清單觀察):

| Application | 用途 | Project 命名 |
|---|---|---|
| `Dev` | 開發版程式碼 | `Dev_<專案名>` |
| `Prod` | 正式版程式碼 | `<專案名>`(無前綴) |
| `Restricted` | 受限系統 | `RS_<專案名>` |
| `Test_CICD` | CI/CD 串接測試 | 不固定 |
| `TMP` / `Demo` | 暫時、示範 | 不固定 |

送 `dev` 分支的程式碼就選 `Dev` / `Dev_<專案名>`,不要送到 `Prod` 的同名 Project。

zip 內容:整個專案目錄,**排除建置產物與版控目錄**,但**保留相依宣告與前端函式庫**
(`.csproj`、`packages.lock.json`、`wwwroot/lib` 等,那些正是 SCA 要看的):

```
7z a -tzip <輸出>.zip . -xr!bin -xr!obj -xr!.vs -xr!.git -xr!logs -xr!node_modules
```

zip 檔名帶上 commit 短 SHA,報告才對得回程式版本。

### Mend 平台(結果查詢)

- 組織:`COTA Commercial Bank, Ltd.`
- 資安總覽:
  `https://saas.mend.io/app/orgs/COTA%20Commercial%20Bank%2C%20Ltd./dashboard/security`
- 專案的 SAST 結果:`.../applications/sast?project=<專案 UUID>`,標題顯示
  `Code Findings (n)`。表格右上角有 **CSV 匯出**(依目前排序、篩選、分組匯出)。
- 點單筆 finding 會開側欄,附完整 data flow(source → sink,逐行程式碼),
  可用動作:**Suppress**、**Mark as In Review**、**Create Issue**;側欄另有
  `Suppression Requests`,表示 Suppress 可能要走核可。
- **修正前後要逐筆比對,不能只看總數**。CSV 的 `Deep Link` 欄尾端帶 finding UUID
  (`...filter_sast_findings_tbl_uuid=contains:<uuid>`),用它比對才分得出「同一批沒變」
  與「舊的消失、新的長出來剛好同數量」。`Date` 欄是該筆最後被重新判定的時間——
  改了程式但該筆仍在,`Date` 會更新,代表工具重新分析過仍判定違規(不是沒掃到)。

### ⚠ 名字寫 SCA,實際跑的是 SAST(Code)

入口叫 `Mendsca`、頁面標題寫 **Mend SCA Scanner**,但**實測送件後在 Mend 平台上
產生的掃描,Scan Engine 是 `Code`(即 SAST)**,結果落在專案的
`Security → Code`(網址 `/applications/sast?project=...`);
同一專案的 `Security → Dependencies` 是 `Direct Libraries 0`、無任何 library
alert,代表**這個入口不會跑相依分析**。

驗證方式:送件後到 Mend 的 `Projects → <專案> → Scans`,看該筆的 Scan Engine 欄。

實務上的意思:

| 你要的 | 這個入口給不給 |
|---|---|
| 自己寫的程式碼缺陷(SQL injection、XSS、Trust Boundary…) | ✅ 給,這正是它在做的 |
| 第三方套件的已知漏洞(CVE/GHSA) | ❌ **不給**,要另外走 Dependencies 掃描 |

所以**別把這個入口的報告當成相依漏洞的交代**。相依漏洞怎麼在公司流程裡送掃
(是否另有入口、或由 Mend 直接接 repo)**待確認**;在那之前,.NET 專案至少要自己
跑下面的預檢。

兩種掃描的差別:

| | 掃什麼 | 典型發現 |
|---|---|---|
| **SAST**(此入口實際做的) | 自己寫的程式碼邏輯缺陷 | Trust Boundary Violation、Error Messages Information Exposure |
| **SCA** | 第三方套件的已知漏洞 | 某套件某版本命中 CVE/GHSA |

### 相依漏洞的本機預檢(此入口不涵蓋)

既然上面那個入口只跑 SAST,相依漏洞就得自己顧。.NET 專案用內建指令自查:

```
dotnet list package --vulnerable --include-transitive
```

它讀 NuGet advisory,列出套件、解析版本、嚴重性與 GHSA 連結。實務上內部專案掃出來
的漏洞多半落在 `CotaUtility.*` 帶進來的**傳遞相依**(而非專案的直接相依),這種要嘛
請套件維護方升版,要嘛在 `.csproj` 加上層級 `PackageReference` 強制覆寫版本——後者
等於繞過內部套件的版本鎖,要先確認相容性。

### Mend AI Reviewer(掃描結果的 AI 複核)

公司自製工具,把 Mend 的 findings 交給行內 LLM(`llm1.cotabank.com` 的 CotaLLM1)
逐案複核,產出「真實風險 / 誤判」判定與理由的 Markdown 報告,可合併匯出 PDF 當
異動單附件。部署包在 `原始碼掃描風險AI輔助評估工具\mend-ai-reviewer-deploy-*`,
裝成 Windows 服務 `mendreviewer`,管理介面 `http://127.0.0.1:3800`。

- 輸入**兩件**:專案原始碼要放在 `<projects_base_dir>\<專案名稱>_<民國年月日>`
  (例 `D:\Compile\AISTT_1150904`),再上傳 Mend 匯出的 CSV。
- 工作台四步驟:指定專案根目錄 → 上傳 findings → 確認內部/外部分類 → 啟動複核。
  報告產在 `<專案根目錄>\RiskAssessmentReport\`,檔名含判定結果
  (`...-FalsePositive-<風險類型>.md`)。
- ⚠ **「使用者補充情境」欄位留空**。填進去等於先把結論餵給複核者,它會照著你的說法
  背書,失去獨立判斷的意義。讓它自己去讀程式碼——實測不給情境時,它會自行去找
  設定檔、搜尋 sink 的讀取點、交叉比對測試專案,挖到的證據反而比人工提示更完整。
  同理,專案裡若有你自己寫的說明文件(如 `CLAUDE.md`),複核前先移除。
- 程式碼註解沒辦法也不需要拿掉——那本來就該留在程式碼裡。
- 部署包分 test / prod 兩種,**檔名完全相同,只有 exe 內建的抄送金鑰不同**,
  靠 SHA-256 分辨(包內 `版本環境-測試.txt` 有宣告值)。更新流程:停服務 → 覆蓋
  `mend_ai_reviewer.exe` → 啟動 → 對雜湊 → 跑 `部署驗收.cmd`。

## 風險評估表與測試報告(異動單附件)

- **風險評估表**:抄程式的人填,送異動單時夾在程式異動管理系統的「相關附件」。
- **測試報告**:抄程式的人填上半部(至測試重點),傳給測試人員填下半部
  (測試項目起),完成後夾在異動單的「測試報告」。
- 範本:入口網 > 文件管理系統 > ISMS-3-003-T07;共用資料夾
  `\\192.168.253.237\0090\UserData\PublicData\第1B組專區\` 有範例。

### 風險評估報告產生器

舊網址 `http://192.168.251.169/cotareport/RiskScore` 現在 **302 轉到
`https://svr134.cotabank.com/CotaReport`**(Windows 整合驗證)。同站還有
**專案上線申請單產生器**(`/CotaReport/Report/GoLive`)與 Anchor 報告產生器。

網頁版是三步驟:上傳抄送清單 txt → 逐檔填風險等級 → 產生 docx。**檔案多時網頁容易當掉**,
可以略過 UI 直接打 API(同樣走整合驗證),輸入輸出跟網頁版完全一樣:

```
POST https://svr134.cotabank.com/CotaReport/api/reports/GenerateReport
Content-Type: application/json

{ "createDate":"yyyy-MM-dd", "creator":"評估人", "reportname":"報告檔名",
  "records":[ {"sequence":1, "codepath":"<專案>/Program.cs",
               "isedited":true, "risklevel":12} ] }
```

回應直接就是 docx(`application/vnd.openxmlformats-...document`)。

- `codepath` 來自異動單「異動檔案區 → 清單匯出」的 txt(一行一個路徑)。
- `isedited`:`true`=修改、`false`=新增。
- `risklevel` 代碼:

| 等級 | 代碼 |
|---|---|
| 高 | 161 (A1) 提供批次交易 / 162 (A2) 批次查詢異動個資機敏 / 163 (A3) 提供交易或個資功能之 Server 程式、函式庫 / 164 (A4) 供客戶操作且涉及 A3 / 169 (A9) 其他對營運有重大影響 |
| 中 | 177 (B1) 直接或間接提供客戶服務 / 178 (B2) 業務交易、會計帳務、對帳單、申報 / 179 (B3) 對外申報(聯徵、央行、檢查局…) / 180 (B4) 同時異動多筆資料 / 181 (B5) 異動資料屬交易紀錄、客戶個資、機敏或金額 / 185 (B9) 其他對營運有較大影響 |
| 低 | 12 (C) 非屬上述狀況 |

風險依**實際異動處**所涉狀況取最高者(定義來源 ISMS-3-003-T11)。純內部員工工具
(不碰客戶服務、交易帳務、對外申報、客戶個資)通常整份都是 C,對應 ISMS-2-002 的
**第三類系統**。

## 程式異動單填寫(CotaIT)

- 新單網址:`https://prjcotait.cotabank.com/CotaIT/webpg/WebpgEdit.aspx?sFun=new`
  (入口網登入態即可進,不必另外登入)。
- **核派單要切「全部」**:預設的「自己」只列你自己是負責人的核派單;專案的核派單負責人
  常常掛在別人身上(例如主管),切「全部」才找得到。勾選後**要再按一次「核派單選定」**
  才會進「已選之核派單號」,系統名稱會跟著自動帶入。
- **異動檔案區 → 選取檔案**:對話框列出抄送目錄。**雙擊**資料夾進入 / `..` 回上層,
  **單擊**選檔(會取代先前選擇),**Ctrl+單擊**才是複選;選好按「添加」加入清單,
  對話框不會關,可以繼續切目錄再加。全部加完按「關閉」。
- ⚠ **異動檔案區的表格只渲染前 12 列**,實際筆數以上方「總異動數」為準
  (完整清單在隱藏欄位 `Selected_Files_Edit`)。別因為表格短就以為漏選。
- ⚠ **抄送目錄不含點開頭的檔案**(`.gitignore` 等選不到),所以 git 的異動檔案數
  可能比實際可抄送的多。
- 「清單匯出」產出的 txt 就是風險評估報告產生器 Step 1 的輸入,順手匯出存好。
- **有清單就用「清單匯入」,不要逐檔點**:把一行一個路徑的 txt(格式同「清單匯出」)
  丟進去,14 筆一次進清單。匯入是走本機元件 `https://localhost:21443/rundll`
  (`UnixFileSelectorX.dll` 的 `Import`)實際到抄送目錄比對,**要等 30 秒上下才回填
  筆數**,這段期間畫面停在「總異動數 0 筆」是正常的,不是卡住。回應的
  `WarningNonExist` 列出抄送目錄裡找不到的路徑,空陣列才代表全部對到。
- 兩個勾選欄的判斷:
  - **揭露個資**:看程式有沒有真的查詢/顯示個資。寫進 Session 但全專案無讀取點的欄位
    不算揭露;但要注意有沒有把含姓名的原始字串輸出到頁面(例如入口網 `hiseed` 以
    hidden input 帶回入口網,其內容前兩段就是員編與姓名)——這種灰色地帶交使用者
    跟資安確認,不要自己認定。
  - **檔案結構或資料庫結構異動**:指資料檔格式或 DB schema 變更,新增程式檔不算。
- **相關附件一次只吃一個檔**,多份要分次上傳(可從 `#AttachmentFileCount` 確認筆數)。
- **填完先按「暫存」**。按暫存前單子只存在瀏覽器裡,重整、分頁關閉或自動化工具斷線
  都會整張消失。暫存成功會配發異動單編號(格式 `<年>-W-<組>-<流水>`,例如
  `2026-W-16-00301`)並轉到續填網址
  `https://prjcotait.cotabank.com/CotaIT/webpg/WebpgEdit.aspx?sfun=edit&pNo=<編號>`,
  之後可以直接回這個網址補測試報告、測試人員與驗收人再送出。

## 緊急抄送

- 申請授權開放時間:**營業日 17:20 過後、非營業日**。
- 有統一的申請方式,COBOL / JAVA / WEB 各有處理流程(見參考頁)。

## 參考

- 專案設定GIT: https://svrconf.cotabank.com/pages/viewpage.action?pageId=64127149
- 【程式抄送】避免漏選檔案的方法: https://svrconf.cotabank.com/pages/viewpage.action?pageId=87360115
- 原始碼檢測: https://svrconf.cotabank.com/pages/viewpage.action?pageId=22282261
- 風險評估表與測試報告: https://svrconf.cotabank.com/pages/viewpage.action?pageId=35880970
- 緊急抄送相關說明: https://svrconf.cotabank.com/pages/viewpage.action?pageId=37683270
