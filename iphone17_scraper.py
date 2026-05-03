import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def run_task():
    print("--- 🔧 銓展自動化系統：啟動檢查 ---")
    
    # 1. 檢查保險箱 (Secret)
    secret_key = "FIREBASE_SERVICE_ACCOUNT"
    raw_json = os.getenv(secret_key)
    
    if not raw_json:
        print(f"❌ 錯誤：在 GitHub Secrets 裡找不到名為 '{secret_key}' 的保險箱！")
        print("💡 請檢查 GitHub -> Settings -> Secrets and variables -> Actions 裡有沒有設定好。")
        return False
    
    # 2. 檢查金鑰格式
    try:
        service_account_info = json.loads(raw_json)
        print("✅ 成功讀取保險箱金鑰。")
    except Exception as e:
        print("❌ 錯誤：保險箱裡的 JSON 格式好像貼錯了！")
        print(f"💡 具體報錯：{e}")
        return False

    # 3. 連線雲端
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ 雲端資料庫連線成功！")
    except Exception as e:
        print(f"❌ 錯誤：無法登入 Firebase。請確認下載的是「服務帳號金鑰」。")
        print(f"💡 具體報錯：{e}")
        return False

    # 4. 執行模擬更新
    app_id = os.getenv('APP_ID', 'VIP-QZ')
    print(f"🚀 正在為專案 [{app_id}] 更新報價...")
    
    models = [
        {"name": "iPhone 17 (256G)", "landmark": 32500, "jiesheng": 32490, "sogi": 32600, "brand": "apple"},
        {"name": "iPhone 17 Pro (256G)", "landmark": 40500, "jiesheng": 40400, "sogi": 40600, "brand": "apple"}
    ]

    for item in models:
        doc_id = item["name"].replace(" ", "_")
        path = f'artifacts/{app_id}/public/data/iphone_prices/{doc_id}'
        db.document(path).set(item, merge=True)
        print(f"📡 {item['name']} 報價上傳成功！")

    print("--- ✨ 全自動任務圓滿完成 ---")
    return True

if __name__ == "__main__":
    if not run_task():
        exit(1) # 讓 GitHub 顯示紅色叉叉，提醒老闆看日誌
