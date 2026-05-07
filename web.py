import requests
import json
import os
import urllib3
from flask import Flask, request
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- 0. 解決 SSL 憑證驗證失敗問題 (重要：解決 road 功能報錯) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. Firebase 初始化 ---
if not firebase_admin._apps:
    try:
        if os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
        else:
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if firebase_config:
                cred_dict = json.loads(firebase_config)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase 初始化失敗：{e}")

app = Flask(__name__)

# --- 2. 路由設定 ---

@app.route("/")
def index():
    homepage = "<h1>洪詩晴 Python 網頁 20260507</h1>"
    homepage += "<p><b>功能測試清單：</b></p>"
    homepage += "<a href='/today'>📅 顯示日期時間</a><br>"
    homepage += "<a href='/weather_input'>☁️ 縣市天氣預報查詢</a><br>"
    homepage += "<a href='/road'>⚠️ 台中市十大肇事路口(洪詩晴)</a><br>"
    homepage += "<a href='/read2'>👤 搜尋老師姓名關鍵字</a><br>"
    return homepage

# (1) road: 列出台中市十大肇事路口
@app.route("/road")
def road():
    R = "<h2>📍 台中市十大肇事路口</h2><hr>"
    try:
        url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
        # 加上 verify=False 解決連線錯誤
        response = requests.get(url, verify=False, timeout=10)
        response.encoding = 'utf-8'
        json_data = response.json()
        
        for item in json_data[:10]:
            R += f"🚩 <b>{item.get('路口名稱', '未知')}</b><br>"
            R += f"主要肇因：{item.get('主要肇因', '無資料')}<br><br>"
        
        R += "<br><a href='/'>返回首頁</a>"
        return R
    except Exception as e:
        return f"讀取路口資料發生錯誤：{str(e)} <br><a href='/'>返回首頁</a>"

# (2) weather: 顯示目前天氣及降雨機率
@app.route("/weather_input")
def weather_input():
    return """
    <h2>🌦️ 全台縣市天氣查詢</h2>
    <form action="/weather_result" method="GET">
        請輸入欲查詢的縣市 (如：臺中市)：
        <input type="text" name="city" value="臺中市">
        <button type="submit">查詢天氣</button>
    </form>
    <br><a href="/">返回首頁</a>
    """
@app.route("/weather_result")
def weather_result():
    # 修正引號與參數取得
    city = request.args.get("city", "臺中市").replace("台", "臺")
    
    # 1. 修正網址：確保 {city} 有正確放在 locationName= 後面
    token = "rdec-key-123-45678-011121314" 
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"
    
    try:
        # 2. 修正連線：加入 verify=False 解決 SSL 錯誤
        res = requests.get(url, verify=False, timeout=10)
        data = res.json()
        
        if "records" in data and data["records"]["location"]:
            loc_info = data["records"]["location"][0]
            # 取得天氣現象 (例如：多雲時晴)
            weather_state = loc_info["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            # 取得降雨機率
            rain_chance = loc_info["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            
            result = f"<h3>📍 {city} 最新天氣預報</h3>"
            result += f"<p>目前天氣狀況：<b>{weather_state}</b></p>"
            result += f"<p>降雨機率：<b>{rain_chance}%</b></p>"
        else:
            result = f"<h3>找不到「{city}」的天氣資料</h3>"
            
        return result + "<br><a href='/weather_input'>重新查詢</a> | <a href='/'>返回首頁</a>"
    except Exception as e:
        # 這裡會捕捉並顯示錯誤訊息
        return f"氣象資料獲取失敗：{e} <br><a href='/'>返回首頁</a>"
# 顯示日期時間
@app.route("/today")
def today():
    now = datetime.now()
    return f"<h3>現在時間：{now.strftime('%Y-%m-%d %H:%M:%S')}</h3><br><a href='/'>返回首頁</a>"

# 老師資料查詢
@app.route("/read2")
def read2_input():
    return """
    <h2>👤 老師查詢系統</h2>
    <form action="/search_result" method="GET">
        姓名關鍵字：<input type="text" name="keyword"> <button type="submit">搜尋</button>
    </form>
    <br><a href="/">返回首頁</a>
    """

@app.route("/search_result")
def search_result():
    keyword = request.values.get("keyword", "").strip()
    try:
        db = firestore.client()
        docs = db.collection("資管二B2026").get()
        res = f"<h3>「{keyword}」搜尋結果：</h3>"
        found = False
        for doc in docs:
            t = doc.to_dict()
            if keyword in t.get("name", ""):
                res += f"<p><strong>{t.get('name')}</strong> - {str(t)}</p>"
                found = True
        if not found: res += "查無資料。"
        return res + "<br><a href='/'>返回首頁</a>"
    except Exception as e:
        return f"錯誤：{e} <br><a href='/'>返回首頁</a>"

if __name__ == "__main__":
    app.run(debug=True)