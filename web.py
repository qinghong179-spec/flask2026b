import requests
import json
import os
import urllib3
from flask import Flask, request,make_response, jsonify
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
# 補上缺少的 BeautifulSoup 引用
from bs4 import BeautifulSoup

# --- 0. 解決 SSL 憑證驗證失敗問題 ---
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
    homepage += "<a href='/rate'>🎬 本週新片進DB</a><br>"
    return homepage

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    #msg =  ["queryResult"]["queryText"]
    #info = "我是洪詩晴設計的機器人動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是洪詩晴設計的機器人,您選擇的電影分級是：" + rate

    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/rate")
def rate():
    # 本週新片爬蟲
    url = "https://www.atmovies.com.tw/movie/new/"
    try:
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        
        # 取得更新日期
        update_tag = sp.find(class_="smaller09")
        lastUpdate = update_tag.text[5:] if update_tag else "未知"

        result = sp.select(".filmList")
        db = firestore.client()

        for x in result:
            try:
                title = x.find("a").text
                introduce = x.find("p").text

                # 處理 ID 與 連結
                link_tag = x.find("a").get("href")
                movie_id = link_tag.replace("/", "").replace("movie", "")
                hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
                picture = f"https://www.atmovies.com.tw/photo101/{movie_id}/pm_{movie_id}.jpg"

                # 處理分級
                r = x.find(class_="runtime").find("img")
                rate_text = "未分級"
                if r:
                    rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
                    rate_dict = {"G": "普遍級", "P": "保護級", "F2": "輔12級", "F5": "輔15級", "R": "限制級"}
                    rate_text = rate_dict.get(rr, "限制級")

                # 處理片長與上映日期 (加入防錯，避免 int() 轉換失敗)
                t_info = x.find(class_="runtime").text
                
                # 抓取片長
                try:
                    t1 = t_info.find("片長")
                    t2 = t_info.find("分")
                    showLength = int(t_info[t1+3:t2].strip())
                except:
                    showLength = 0

                # 抓取日期
                try:
                    d1 = t_info.find("上映日期")
                    # 避免切片範圍錯誤，改用較彈性的找法
                    showDate = t_info[d1+5:d1+15].strip() 
                except:
                    showDate = "未知"

                doc = {
                    "title": title,
                    "introduce": introduce,
                    "picture": picture,
                    "hyperlink": hyperlink,
                    "showDate": showDate,
                    "showLength": showLength,
                    "rate": rate_text,
                    "lastUpdate": lastUpdate
                }

                # 寫入 Firebase
                doc_ref = db.collection("本週新片含分級B").document(movie_id)
                doc_ref.set(doc)
            except Exception as inner_e:
                print(f"單部電影處理失敗: {inner_e}")
                continue

        return f"✅ 本週新片已爬蟲及存檔完畢！最近更新日期：{lastUpdate} <br><a href='/'>返回首頁</a>"

    except Exception as e:
        return f"❌ 發生錯誤：{e} <br><a href='/'>返回首頁</a>"

# (1) road: 列出台中市十大肇事路口
@app.route("/road")
def road():
    R = "<h2>📍 台中市十大肇事路口</h2><hr>"
    try:
        url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
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

# (2) weather: 查詢天氣
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
    city = request.args.get("city", "臺中市").replace("台", "臺")
    token = "rdec-key-123-45678-011121314" 
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"
    
    try:
        res = requests.get(url, verify=False, timeout=10)
        data = res.json()
        
        if "records" in data and data["records"]["location"]:
            loc_info = data["records"]["location"][0]
            weather_state = loc_info["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            rain_chance = loc_info["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            
            result = f"<h3>📍 {city} 最新天氣預報</h3>"
            result += f"<p>目前天氣狀況：<b>{weather_state}</b></p>"
            result += f"<p>降雨機率：<b>{rain_chance}%</b></p>"
        else:
            result = f"<h3>找不到「{city}」的天氣資料</h3>"
            
        return result + "<br><a href='/weather_input'>重新查詢</a> | <a href='/'>返回首頁</a>"
    except Exception as e:
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