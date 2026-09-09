# 重構盤點

來源：根目錄 index.html，包含 AI Salesman 主畫面與 V2 人物預覽；其餘 HTML 屬其他專案，未更動。

原始 SHA-256：ce5e6e106ee91bf6c5b3e2d52fcddaa39fa407961b58b18b1a127c361d0a2bde

原功能：六種業務人格、人物外觀、產品／話術編輯、訓練草稿、沉浸預覽、聊天示範、員工抽屜、網站預覽、ROI 計算、localStorage、JSON 匯出。舊版聊天／匯入為示範，保存在 /legacy-studio，不冒充真實功能。

已抽出 13 個內嵌圖片，保留原 CSS 和 JavaScript。正式本機版以相同品牌、側欄、設定區及人物預覽架構延伸；新人物依新版要求使用參數 SVG。

外部 URL（靜態盤點，包含文字／連結，非全為請求）：
https://yourcompany.com
https://yourcompany.com。

秘密檢查另由 scripts/secret_scan.py 執行；不讀取任何認證儲存檔。
