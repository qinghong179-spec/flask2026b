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
    homepage += "<a href='/spider1'>爬取子青老師本學期課程</a><br>"
    homepage += "<a href='/m1'>爬取即將上映電影</a><br>"
    return homepage

@app.route("/today")
def today():
    now = datetime.now()
    return f"<h3>現在時間：{now.strftime('%Y-%m-%d %H:%M:%S')}</h3><br><a href='/'>返回首頁</a>"

# --- 3. 電影爬蟲功能 ---
@app.route("/m1")
def movie1():
    keyword = request.args.get("keyword", "")
    
    # 注意：這裡的 action 要改成 /m1 才能送回同一個頁面搜尋
    R = f'''
        <div style="font-family: sans-serif; padding: 20px;">
            <h2>電影查詢系統</h2>
            <form action="/m1" method="get">
                <input type="text" name="keyword" placeholder="請輸入片名關鍵字" value="{keyword}">
                <button type="submit">搜尋</button>
            </form>
            <hr>
    '''
    
    url = "https://www.atmovies.com.tw/movie/next/"
    try:
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".filmListAllX li")
        
        for item in result:
            a_tag = item.find("a")
            img_tag = item.find("img")

            if a_tag and img_tag:
                movie_name = img_tag.get("alt")
                
                # 關鍵字篩選
                if keyword.lower() in movie_name.lower():
                    movie_url = "https://www.atmovies.com.tw" + a_tag.get("href")
                    img_src = "https://www.atmovies.com.tw" + img_tag.get("src")
                    
                    R += f'''
                        <div style="margin-bottom: 40px;">
                            <h3>{movie_name}</h3>
                            <a href="{img_src}" target="_blank">
                                <img src="{img_src}" width="200" title="點擊看大圖" style="border: 2px solid #ddd; border-radius: 5px;">
                            </a>
                            <p>
                                <a href="{movie_url}" target="_blank" style="text-decoration: none; color: #E44D26; font-weight: bold;">
                                    🔗 點此查看《{movie_name}》詳細介紹
                                </a>
                            </p>
                            <hr>
                        </div>
                    '''
    except Exception as e:
        R += f"發生錯誤：{e}"

    R += "<br><a href='/'>返回首頁</a></div>"
    return R

# --- 4. 老師查詢功能 ---

@app.route("/read2")
def read2_input():
    html = """
    <h2>靜宜資管老師查詢系統</h2>
    <form action="/search_result" method="GET">
        <p>請輸入要搜尋的老師姓名關鍵字：
        <input type="text" name="keyword" placeholder="例如：楊">
        <button type="submit">開始查詢</button></p>
    </form>
    <br><a href="/">返回首頁</a>
    """
    return html

@app.route("/search_result")
def search_result():
    keyword = request.values.get("keyword", "").strip()
    if not keyword:
        return "您沒有輸入關鍵字！<br><a href='/read2'>重新查詢</a>"

    try:
        db = firestore.client()
        collection_ref = db.collection("資管二B2026")
        docs = collection_ref.get()

        found_count = 0
        table_html = f"<h3>關於「{keyword}」的搜尋結果：</h3>"
        table_html += """
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 10px; }
            th { background-color: #2196f3; color: white; }
        </style>
        <table><tr><th>老師姓名</th><th>詳細資料</th></tr>
        """

        for doc in docs:
            teacher = doc.to_dict()
            if keyword in teacher.get("name", ""):
                found_count += 1
                table_html += f"<tr><td><strong>{teacher.get('name')}</strong></td><td>{str(teacher)}</td></tr>"
        
        table_html += "</table>"

        if found_count == 0:
            return f"查無姓名包含「{keyword}」的老師資料。<br><a href='/read2'>重新查詢</a>"

        return table_html + f"<br><p>共找到 {found_count} 筆資料</p><a href='/'>返回首頁</a>"
    except Exception as e:
        return f"資料庫讀取出錯：{str(e)}"

# --- 5. 啟動伺服器 (務必放在最後面) ---
if __name__ == "__main__":
    app.run(debug=True)