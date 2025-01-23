警告:此外掛僅兼容4.3.2以後之版本的blender
安裝與使用
安裝外掛
將此插件的壓縮包（ZIP 文件）下載到本地。
在 Blender 中：
打開 編輯 > 偏好設定 > 外掛。
點擊 安裝，選擇下載的 ZIP 文件。
安裝完成後，勾選 啟用外掛。
配置 API Key
在工具面板中，找到 GPT Assistant。
點擊 Set API Key，輸入您的 OpenAI API Key（可於 OpenAI 官網 獲取）。
獲取後您必須於下列url支付十美金才能獲取讓API能夠啟用並處於工作狀態的積分。
https://platform.openai.com/settings/organization/billing/overview
點擊 保存 即完成設定。
運行外掛
在 工具面板 > GPT Assistant 中，輸入您需要執行的任務或指令：
指令範例：
mathematica
複製
編輯
在 3D 游標位置生成一個立方體，並應用紅色材質。
問題範例：
複製
編輯
如何在 Blender 中優化場景效能？
點擊 Run GPT Command，插件將請求 GPT 並自動執行生成的腳本。
在系統控制台查看執行的腳本及其輸出。
外掛架構
核心功能
與 GPT 模型交互：
插件通過 sync_fetch_gpt_response 與 OpenAI API 通信，獲取 GPT 返回的內容。
代碼清理與驗證：
提取返回的 Python 代碼塊，清理潛在問題字符，並使用 ast 模組驗證代碼合法性。
腳本保存與執行：
生成的腳本會保存至臨時文件，並通過 Blender 的內建 API 自動執行。
文件結構
__init__.py：插件主程式，包含所有功能邏輯。
README.md：自述文件，介紹插件的使用與特性。
面板與操作類
GPT_PT_Panel：提供用戶界面，包含指令輸入框及執行按鈕。
GPT_OT_ExecuteCommand：處理用戶輸入的主邏輯，負責請求 GPT 並調用執行腳本。
GPTAddonPreferences：提供 API Key 的保存與設置功能。
常見問題
1. GPT 返回的腳本無法執行？
請檢查指令是否具體並符合 Blender 的功能範疇。
確保 API Key 有效且未超出使用配額。
2. 如何查看執行結果？
打開 Blender 的 系統控制台，可查看 GPT 返回的代碼以及執行的詳細信息。
3. 支援哪些版本的 Blender？
插件設計時針對 Blender 4.3.2，若需支援其他版本，可能需進行適配。
未來改進
支持多模型選擇：允許用戶選擇不同的 GPT 模型（如 gpt-4-turbo）。
腳本預覽模式：在執行前展示 GPT 返回的腳本，允許用戶手動修改。
多語言支持：為插件提供多語言界面（例如英文、日文等）。
