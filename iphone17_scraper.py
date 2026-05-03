import os
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore

# 這段程式碼負責把資料抓回來並送到雲端
def run_task():
    print("--- 🔧 銓展自動化引擎啟動 ---")
    
    # 讀取保險箱裡的 Firebase 金鑰
    service_account_raw = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    if not service_account_raw:
        print("❌ 錯誤：找不到金鑰，請檢查 GitHub Secrets 設定。")
        return False
    
    # 初始化連線
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(service_account_raw))
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ 成功連線至雲端資料庫。")
    except Exception as e:
        print(f"❌ 連線失敗：{e}")
        return False

    # 模擬抓取數據 (老闆，這裡就是以後要換成爬蟲的地方)
    # 我們先確保數據能成功送上雲端
    models = [
        {"name": "iPhone 17 (256G)", "landmark": 32500, "jiesheng": 32490, "sogi": 32600, "brand": "apple"},
        {"name": "iPhone 17 Pro (256G)", "landmark": 40500, "jiesheng": 40400, "sogi": 40600, "brand": "apple"},
        {"name": "Galaxy S25 Ultra", "landmark": 38500, "jiesheng": 38300, "sogi": 38600, "brand": "samsung"}
    ]
    
    app_id = os.getenv('APP_ID', 'VIP-QZ')

    for item in models:
        doc_id = item["name"].replace(" ", "_")
        path = f'artifacts/{app_id}/public/data/iphone_prices/{doc_id}'
        db.document(path).set({
            **item,
            "last_update": firestore.SERVER_TIMESTAMP
        }, merge=True)
        print(f"📡 {item['name']} 報價已更新到網頁！")

    print("--- ✨ 任務完成 ---")
    return True

if __name__ == "__main__":
    run_task()
