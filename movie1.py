import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 讓使用者輸入關鍵字
keyword = input("請輸入想要查詢的電影片名關鍵字：")

# 查詢資料庫中符合關鍵字的電影
# 注意：Firestore 原生查詢僅支援完全符合或前綴符合
# 這裡先抓取所有電影，再用 Python 進行關鍵字篩選
docs = db.collection("電影2B").stream()

print(f"\n--- 關鍵字「{keyword}」的查詢結果 ---")
found = False

for doc in docs:
    movie = doc.to_dict()
    # 檢查片名是否包含關鍵字
    if keyword in movie.get("title", ""):
        found = True
        print(f"編號：{doc.id}")
        print(f"片名：{movie.get('title')}")
        print(f"海報：{movie.get('picture')}")
        print(f"介紹頁：{movie.get('hyperlink')}")
        print(f"上映日期：{movie.get('showDate')}")
        print("-" * 30)

if not found:
    print("查無符合關鍵字的電影。")