# 張庭瑋醫師個人網站

正式網址：https://drchangtingwei.com/ 。以 GitHub Pages 發布的靜態網站，無需建置套件。

## 維護與檢查

- `index.html`：首頁與依問題分流入口。
- `thoracic/`、`esophageal/`、`bariatric/`：肺部胸腔、食道逆流、代謝減重主題。
- `articles/`：衛教文章；分類搜尋是漸進增強，所有文章文字與連結均存在 HTML 中。
- `appointment/`、`prepare/`：院方掛號、看診準備與手術評估提問清單。
- `styles.css`：原有元件；`patient-navigation.css`：全站分流與響應式補充；`script.js`：選單及本機文章搜尋。

使用 `python3 -m http.server 8832 --bind 127.0.0.1` 預覽。發布前執行 `python3 scripts/check-site.py`，檢查內部連結、錨點、圖片替代文字、JSON-LD、canonical 與 sitemap 一致性，並實測手機選單與掛號連結。

新增頁面須同步 `sitemap.xml`、`sitemap.txt`、`llms.txt` 與 `.github/workflows/indexnow.yml`。重大內容變更才更新對應頁面日期；導覽修改不代表醫師重新審閱臨床內容。`.tmp/` 是本機測試與截圖，不應提交或發布。

本院掛號入口需確認「張庭瑋」與診次。岡山使用院方胸腔外科掛號表，進入後選「夜間診」及週四「張庭瑋」；醫師簡介仍保留供核對。開診、額滿、停代診與費用以院方為準。

搜尋字詞僅在瀏覽器內比對，不儲存或傳送；本站不蒐集病歷或預約身分資料。既有 gtag 事件僅在另行設定分析服務後生效，按鈕點擊不代表完成掛號。可參考同業架構，但不複製照片、文字或成效宣稱，也不保證搜尋排名或 AI 推薦。

## 初版建置紀錄（歷史資料）

以下為初版規劃備忘，正式網域、掛號入口與現行架構以上方說明及實際頁面為準。

這是一個可直接開啟的靜態個人網站草稿，主軸是張庭瑋醫師的胸腔外科與代謝減重外科門診導流。首頁已包含手機版導覽、門診 CTA、SEO meta、Open Graph、Schema.org Physician 結構化資料、`robots.txt` 與 `sitemap.xml`。

## 預覽

直接開啟 `index.html` 即可預覽。正式上線前請先替換下列資料。

## 需要提供的正式資料

1. 網站正式網域，例如 `https://yourname.com`。
2. 是否要新增英文姓名、英文簡介或英文 SEO。
3. 是否有更正式的首頁橫式形象照，可取代目前生成的非真人醫療情境圖。
4. 是否要加入更多衛教文章，例如肺結節追蹤、減重手術術式比較、術後飲食照護。
5. 是否有其他社群連結，例如 Instagram、Threads、YouTube 或 LinkedIn。

## 上線前建議

1. GitHub Pages 預設網址已設定為 `https://drchangtingwei-code.github.io/`；若未來購買正式網域，再把這個網址全部換成正式網域。
2. 確認門診時段、掛號電話與院方連結是否仍為最新資訊。
3. 將 `assets/hero-consultation.jpg` 替換成授權可用的正式橫式照片，或保留目前生成圖作為非真人形象視覺。
4. 到 Google Search Console 提交 `sitemap.xml`。
5. 建立或更新 Google Business Profile，讓地圖搜尋與門診資訊互相連結。

## 內容提醒

醫療網站建議避免療效保證、誇大比較、未授權病人故事、術前術後照與個資揭露。衛教內容應保持一般性，個別診斷與治療建議仍以門診評估為準。

## 已參考公開資料

1. Facebook 粉絲專頁：張庭瑋醫師-代謝減重/胸腔外科。
2. 高雄醫學大學附設中和紀念醫院醫師介紹頁：醫師代碼 `1080224`。
