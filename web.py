import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. Firebase 初始化 ---
if not firebase_admin._apps:
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    else:
        firebase_config = os.getenv('FIREBASE_CONFIG')
        if firebase_config:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

app = Flask(__name__)

# --- 2. 路由設定 ---

@app.route("/")
def index():
    homepage = "<h1>洪詩晴Python網頁20260409</h1>"
    homepage += "<a href='/today'>顯示日期時間</a><br>"
    homepage += "<a href='/read2'>搜尋老師姓名關鍵字</a><br>"
    homepage += "<a href='/spiderMove'>爬取即將上映電影至資料庫</a><br>"
    homepage += "<a href='/movie_query'>🔍 查詢資料庫電影 (關鍵字)</a><br>"
    return homepage

@app.route("/today")
def today():
    now = datetime.now()
    return f"<h3>現在時間：{now.strftime('%Y-%m-%d %H:%M:%S')}</h3><br><a href='/'>返回首頁</a>"

# --- 3. 電影功能：爬取並存入資料庫 ---
@app.route("/spiderMove")
def spiderMove():
    try:
        db = firestore.client()
        url = "http://www.atmovies.com.tw/movie/next/"
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        
        lastUpdate = sp.find(class_="smaller09").text.replace("更新時間:", "").strip()
        result = sp.select(".filmListAllX li")
        
        total = 0
        for item in result:
            total += 1
            movie_id = item.find("a").get("href").replace("/movie/","").replace("/","")
            title = item.find(class_="filmtitle").text
            picture = "https://www.atmovies.com.tw" + item.find("img").get("src")
            hyperlink = "https://www.atmovies.com.tw" + item.find("a").get("href")
            showDate = item.find(class_="runtime").text[5:15]

            doc = {
                "title": title,
                "picture": picture,
                "hyperlink": hyperlink,
                "showDate": showDate,
                "lastUpdate": lastUpdate
            }
            db.collection("電影2B").document(movie_id).set(doc)

        return f"<h3>爬取完成！</h3>網站更新：{lastUpdate}<br>已將 {total} 部電影存入資料庫。<br><a href='/'>返回首頁</a>"
    except Exception as e:
        return f"發生錯誤：{str(e)}"

# --- 4. 電影功能：資料庫關鍵字查詢 ---
@app.route("/movie_query")
def movie_query():
    # 取得搜尋關鍵字
    keyword = request.args.get("keyword", "").strip()
    
    html = f'''
        <div style="font-family: sans-serif; padding: 20px;">
            <h2>🎬 電影資料庫查詢系統</h2>
            <form action="/movie_query" method="get">
                <input type="text" name="keyword" placeholder="請輸入片名關鍵字" value="{keyword}" style="padding:5px; width:250px;">
                <button type="submit" style="padding:5px 15px;">搜尋</button>
            </form>
            <hr>
    '''
    
    if keyword:
        try:
            db = firestore.client()
            # 抓取資料庫所有資料進行篩選
            docs = db.collection("電影2B").stream()
            found_count = 0
            
            for doc in docs:
                movie = doc.to_dict()
                if keyword.lower() in movie.get("title", "").lower():
                    found_count += 1
                    html += f'''
                        <div style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                            <p><strong>編號：</strong>{doc.id}</p>
                            <p><strong>片名：</strong>{movie.get('title')}</p>
                            <p><strong>上映日期：</strong>{movie.get('showDate')}</p>
                            <a href="{movie.get('hyperlink')}" target="_blank">
                                <img src="{movie.get('picture')}" width="150" style="border-radius:5px; display:block; margin: 10px 0;">
                                點此查看詳細介紹頁
                            </a>
                        </div>
                    '''
            
            if found_count == 0:
                html += f"<p>查無符合「{keyword}」的電影資料。</p>"
            else:
                html += f"<p>共找到 {found_count} 筆搜尋結果。</p>"
                
        except Exception as e:
            html += f"查詢出錯：{str(e)}"
    else:
        html += "<p>請在上方輸入框輸入關鍵字開始搜尋。</p>"

    html += "<br><a href='/'>返回首頁</a></div>"
    return html

# --- 5. 老師查詢功能 (保留原功能) ---
@app.route("/read2")
def read2_input():
    return """
    <h2>靜宜資管老師查詢系統</h2>
    <form action="/search_result" method="GET">
        <p>請輸入要搜尋的老師姓名關鍵字：
        <input type="text" name="keyword" placeholder="例如：楊">
        <button type="submit">開始查詢</button></p>
    </form>
    <br><a href="/">返回首頁</a>
    """

@app.route("/search_result")
def search_result():
    keyword = request.values.get("keyword", "").strip()
    if not keyword: return "未輸入關鍵字！<br><a href='/read2'>返回</a>"
    try:
        db = firestore.client()
        docs = db.collection("資管二B2026").get()
        found_count = 0
        res = f"<h3>「{keyword}」搜尋結果：</h3>"
        for doc in docs:
            t = doc.to_dict()
            if keyword in t.get("name", ""):
                found_count += 1
                res += f"<p><strong>{t.get('name')}</strong> - {str(t)}</p>"
        return res + f"<p>共 {found_count} 筆</p><a href='/'>首頁</a>"
    except Exception as e: return f"錯誤：{e}"

if __name__ == "__main__":
    app.run(debug=True)