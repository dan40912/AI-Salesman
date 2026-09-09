# 驗證紀錄 · 2026-09-09

## 已執行與通過

- 原根目錄 `index.html` 與 `legacy/AI-Salesman.original.html` 的 SHA-256 相同；原檔未覆寫。13 個 base64 圖片抽出，正式前端無內嵌大型圖片。Codex 專用 runtime 目錄為空。
- `./run-local.sh` 成功啟動 Uvicorn，監聽 `127.0.0.1:8000`。前台、後台、設定頁、OpenAPI JSON 與本機 `/docs` 可讀取。
- `.venv/bin/python -m unittest discover -s tests -v`：**15 組測試全部通過**。包含 mock 串流與資料保存、角色新增修改停用、avatar 範圍驗證、5 場景／8 預設、TXT／DOCX／PDF 解析、FTS 檢索、hash 去重、刪除原檔與來源、圖片重編碼、惡意檔名／MIME／過大檔案拒絕、Host／Origin／跨站限制、結構化輸出降級、6 類情境、拒絕內容不微笑、工具／process／filesystem RPC 拒絕、模擬斷線仍可讀本機資料。
- `node --check frontend/app.js`、`node --check frontend/avatar.js`：通過。
- `.venv/bin/python scripts/secret_scan.py`：來源及專案 Git 追蹤檔案的模式掃描，**0 個疑似秘密**。不讀取憑證儲存檔、被忽略的使用者資料或 Git 歷史；不是完整資安稽核。
- `.venv/bin/python tests/live_smoke.py --run`：使用官方 ChatGPT Pro 訂閱，**RAG 真實串流、刪除後不再引用、角色切換、停止生成、macOS WAV 與相同音訊快取全部通過**。測試用合成文件與該測試建立的對話已清除。
- 最新取消清理修改後，另外實際執行一段短對話並於 started 中斷：收到 conversation → started → 停止錯誤，沒有 done；之後可以清除對話。API 文件使用本機 JS，沒有外部 CDN。
- 官方 `account/read` 實測為 ChatGPT / pro；`model/list` 回報 6 個模型，`account/rateLimits/read` 成功。沒有使用 API key、取得或消耗 reset credit。
- 瀏覽器端成功顯示真實回覆。macOS 音訊 `<audio>` duration / currentTime 均為 **7.281315 秒**，ended=true、error=null，播放結束後回到 idle。
- 桌面前台、Avatar Studio 8 個人物縮圖與管理欄位已視覺檢查；選擇第 6 個人物後即時變更臉型、五官、髮髻、眼鏡及服裝。介紹產品／停止動作按鈕可操作。
- 390 × 844 手機前台已實際截圖檢查，單欄排版、導覽與人物區正常；檢查後恢復原瀏覽器尺寸。

## 限制與待人工驗收

- **尚未完成全部規格驗收。** 麥克風沒有代替使用者授權或實際說話；STT 真實收音、辨識準確度與供應商處理方式需在你使用的瀏覽器測試。API 存在不等於辨識服務一定可用。
- macOS WAV 播放已驗證；瀏覽器 Speech Synthesis 備援的聲音品質與 boundary 行為未完整人工驗收。沒有聲音時可使用文字，或改回已測試的 macOS 模式。
- 六類情境的後端規則有測試；所有動畫在不同瀏覽器中的逐幀表現、停止後零殘留的完整矩陣未全部錄影驗證。瀏覽器自動化讀取部分動畫狀態時遇到工具逾時，因此沒有假稱該項全面通過。
- 真實斷網沒有切斷這台電腦的網路；已測試模擬連線失敗的錯誤路徑與本機資料存取。登入逾期、方案無權限、實際耗盡額度也未刻意觸發。
- CLI 相容性以 0.153.4 為準。已驗證 feature 覆寫與 MCP 設定、拒絕請求的程式路徑，但不是對所有未來 CLI 版本或所有 prompt injection 的形式化證明。
- 原 V2 的示範互動保存於獨立 `/legacy-studio`，其 mock 匯入／訓練／網站預覽沒有轉成真實第三方整合。正式頁面使用 SQLite 的四個亞洲虛構角色與新 2D 動畫。
- 測試工具顯示 Starlette 對 httpx TestClient 的棄用提醒，未造成測試失敗；正式執行不使用 TestClient。

完整啟動、資料清除、外部網路與已知限制請見 `README.md`。下一個驗收步驟是你在瀏覽器點麥克風、說一句話、送出，再於播放中按「停止」。
