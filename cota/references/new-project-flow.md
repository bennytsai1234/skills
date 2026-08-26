# 新專案標準開發流程(端到端預設骨架)

新開一個內部 .NET Web 專案時,「該走哪些流程、哪些東西是標配」的整合視圖。
各細節在對應 reference,這裡是把它們串成一條線,並釐清哪些是**預設就要有**、
不是「要不要導入」的選項。使用者問「以後開發流程」「新專案標準怎麼跑」「需不需要
測試環境 / staging」「要不要走完整那一套」時查這裡。

## 預設立場:完整流程是預設,精簡才需要理由

內部專案**預設就走公司完整流程**——雙環境抄送、前台雙機高可用、多機時 Redis 共享狀態、
接監控看板。不是逐項評估「要不要導入」;要偏離(例如單機、不接看板)才需要明確理由與
使用者決定。掃描或開案時的預設姿態是「照標準跑」,不是「先問要不要」。

> **雙機高可用有兩種擺法,公司都支援:AA(Active/Active,兩台同時服務)與
> AP(Active/Passive 主備,一台服務、一台待命,故障切換)。** 預設姿態是「要雙機」,
> 但 AA 還是 AP **由專案自己決定、不是硬性規定**——skill 與 Confluence 都沒有明訂
> 「該選哪個」的準則,實務上是每專案在上線申請表勾「Active/Active 模式服務:啟用/
> 不啟用」+ 系統組在 HAProxy 設定(active/active 或 active/backup)來決定。開案時
> 要把 AA 與 AP 的取捨攤給使用者選,不要預設替他勾 AA。兩者的工程差異見第三節。

## 一、環境骨架:測試 + 正式,雙軌是預設(這就是 staging)

公司用 Gogs 分支對應環境,測試環境是**內建**的,不是額外選項:

| 分支 | 效果 |
|---|---|
| `dev`(注意大小寫) | 同步到**測試環境**抄送目錄 |
| `master` | 同步到**正式環境**抄送目錄 |

- 「需不需要 staging」在公司框架下不成立——`dev` 抄送那台就是測試環境。
- 本機修改開自己的分支,上測試才併 `dev`,上線才併 `master`,讓 `master` 只留上線版本。
- `master` 紀錄不可刪、不支援 `--force`,退版一律 `git revert`。
- 分支/抄送/異動單細節見 `references/git-workflow.md`。

## 二、兩次申請,分開辦

1. **開發申請** → 管理組＋系統組配開發機、AP User、HostName。
2. **上線申請** → 上線前辦,系統組會拿開發申請表核對。

> 「無論將來放 HA 或 AA 主機,都需先填申請表;開發與正式上線分開申請。」
> 前台雙機在申請表就要勾:**Active/Active 模式服務=啟用**、**HAProxy=啟用**。
> 申請單完整欄位(逐欄填寫)見 `references/web-platform.md`。

## 三、前台雙機高可用是預設(AA 或 AP)→ 多機時 Redis 變標配

公司預設**前台請求層要雙機高可用**,擺法有 AA 與 AP 兩種(見「預設立場」的說明,兩種都
支援、由專案選)。一旦多機,下列從「可選」升為「標配」——但**要共享多少狀態,AA 跟 AP
差很多**,先分清楚:

### AA 與 AP 的工程差異(決定要搬多少東西上 Redis)

- **AA(兩台同時服務)**:同一時間兩台都在收 request,狀態會**即時分裂**——「甲台記的
  乙台不知道」。所以**所有跨機即時狀態都得共享**:Session、in-memory presence/連線登記、
  跨機命令路由(SignalR 要 Redis backplane)、in-memory 佇列協調、執行期設定的跨機失效
  廣播(CotaRedisPubSub)。改動最大。
- **AP(主備,一台服務一台待命)**:任一刻只有一台在服務,平時**不會狀態分裂**,故
  presence/佇列/命令路由這些**即時分裂問題大多不發生**(待命台沒在服務);故障切換時
  in-memory 狀態會短暫遺失再自動重建(用戶端重連即補回)。改動小很多。Session 放 Redis
  仍建議(切換時使用者不用重登),但不像 AA 那樣是硬需求。
- **兩者都躲不掉的一件事:本機檔案/產物要放共享儲存。** 掛掉那台的本機硬碟接手台拿不到,
  所以落在本機檔案系統的東西(上傳圖檔、報表產物等)不論 AA/AP 都要移到共享位置(網路
  共享磁碟 UNC,或落 DB/物件儲存)。

### 多機標配項(依上面差異取用)

- **Session / Cache → CotaRedis**(不可 in-memory,否則兩台各存各的)→ 要**申請
  RedisDB 帳號**(帳號＝專案名大寫,選內部/DMZ/核心區)。見 `references/cota-redis.md`。
  (AA:Session＋跨機共享狀態全需;AP:Session 建議、其餘視需求。)
- **DataProtection 金鑰圈不可綁 DPAPI**(DPAPI 綁機器):改憑證或 Redis 保護,
  否則接手台解不開另一台加密的資料(API 金鑰、antiforgery token 等)。AA/AP 都需要。
- **HAProxy 前置** → 來源 IP 不可直接讀 `RemoteIpAddress`,要走
  `CotaNetwork.GetClientIP`(帶 HAProxy 主機名),否則 per-IP 限流會退化成「全部同一個
  代理 IP」。**前提是專案真的用來源 IP 做白名單/限流**;沒有這類邏輯就用不到,不必硬加。
  見 `references/network.md`。
- **共享儲存**:本機檔案產物移到 UNC 共享(需系統組開 share、授權 AP User)或落 DB。
- **DB**:svrdb + SSPI 整合驗證,連線字串不帶帳密;正式/測試各一個 DB。
  多機時 `db.Database.Migrate()` 開機自動套用會競態,改由部署階段單次套用。
  見 `references/cota-db.md`。

> **「前台雙機」只保證請求層可用性,不等於背景批次能無腦雙跑。** 有 in-memory
> 佇列、單進程復原假設(啟動全清 running 標記)、in-memory 取消登記,或 DPAPI 綁機
> 金鑰的背景服務,直接開兩台會**重複處理、取消失效、金鑰不通**。標準做法是
> **前台雙機 ＋ 背景單一 worker,佇列/取消改走 Redis 協調**,不是兩台都跑背景。
> 這一層在設計時就要分清:前台可用性 ≠ 背景可並行。看不出背景能否並行時標「待確認」。
> (注意:排程若是由用戶端/外部裝置自己觸發、主機只被動接收,就沒有主機端重複觸發問題
> ——盤點時先確認排程的觸發方是誰,不要假設一定是主機在催。)

參考:**WEB Server Active/Active**(AA 做法:兩台 + HAProxy 依序分發 + CotaRedis 存
Session): https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511127

## 四、抄送與異動單(每次上線都走)

1. 上線前**一定看差異比對**;先用 GIT 檔案清單小工具產「異動檔案列表」再逐項檢查
   (避免漏選 NuGet/csproj/dll)。
2. **Checkmarx SCA** 原始碼掃描(`https://sca.cotabank.com/CotaSCA/`,7-Zip 壓 zip 送掃)。
3. 異動單附兩份:**風險評估表**(抄程式的人填)＋**測試報告**(上半抄送者、下半測試人員)。
4. 抄送完 `git tag` 記 online 版本,再 `git push origin <tag>`。
5. 緊急抄送只在營業日 17:20 後／非營業日開放。

細節見 `references/git-workflow.md`。

## 五、監控與資安(上線專案必接)

- **CotaPerformanceCounter + CotaHealthCheckCore** → 接資訊看板[專案監控],才有推播＋
  語音告警;申請表填 `GetProjectInfo`／`GetExtraServices`／狀態檢查 URL。
  見 `references/performance-counter-healthcheck.md`。
  (全站有 Windows 驗證時,監控端點要 `.AllowAnonymous()`,否則 svrotr 來 ping 會 401。)
- **HSTS**:max-age ≥ 1 年 + includeSubDomains(缺任一項被資安列風險)。
- Cookie 政策 `Secure=Always`、`HttpOnly=Always`;CSP header;參數竄改(直接物件參考)
  的輸入驗證。見 `references/web-platform.md` 的資安掃描段。

## 六、身分入口

新專案身分入口走**員工入口網串接(CotaPortal,JWT)**——進站驗 token 取 EmpNo、
回入口網按鈕。舊的 hiseed/RSASign 不用;需要標準 OIDC 才評估 KeycloakAdapter。
見 `references/cota-portal.md`;角色查詢照舊走 PermProvider(`references/perm-provider.md`)。

## 開案檢查清單(照這條線走一遍)

- [ ] Gogs 建倉庫 → 轉移所有權給組織(研發組 `Research` 等)
- [ ] 目標 Framework 確認(net8.0),CotaNuGet 私有來源設好(`references/nuget-setup.md`)
- [ ] 辦**開發申請**(開發機、AP User、HostName)
- [ ] DB 走 svrdb + SSPI;正式/測試兩個 DB
- [ ] 雙機擺法:跟使用者確認走 AA(Active/Active)或 AP(主備)——公司都支援,不預設替他勾
- [ ] 前台雙機標配:CotaRedis Session/Cache + 申請 RedisDB 帳號;金鑰圈脫離 DPAPI
      (AA:Session＋跨機共享狀態全需;AP:Session 建議、其餘視需求)
- [ ] 共享儲存:本機檔案產物移到 UNC 共享或落 DB(AA/AP 都要)
- [ ] HAProxy:若專案用來源 IP 做白名單/限流,Client IP 走 CotaNetwork;確認信任代理網段
- [ ] 背景服務盤點:能否跟前台一起雙跑?不能 → 拆單一 worker + Redis 協調
- [ ] 身分入口:CotaPortal 串接;角色 PermProvider
- [ ] 監控:CotaHealthCheckCore + PerformanceCounter 接看板
- [ ] 資安:HSTS、Cookie 政策、CSP、Checkmarx 掃描過
- [ ] 辦**上線申請**(正式機;AA→「Active/Active 模式服務=啟用」+ HAProxy=啟用,
      AP→依系統組主備設定);逐欄填 `references/web-platform.md`
- [ ] 抄送:`dev` 上測試 → `master` 上正式;異動單附風險評估表 + 測試報告;tag 記版本

## 參考

- WEB專案開發/上線申請: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82511273
- WEB專案上線申請流程: https://svrconf.cotabank.com/pages/viewpage.action?pageId=82510181
- Web應用程式部署流程: https://svrconf.cotabank.com/pages/viewpage.action?pageId=119177262
- 專案設定GIT: https://svrconf.cotabank.com/pages/viewpage.action?pageId=64127149
