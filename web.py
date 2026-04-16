import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Firebase 初始化
if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    if firebase_config:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = None

if cred and not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

app = Flask(__name__)

# --- 路由設定 ---

@app.route("/")
def index():
    homepage = "<h1>洪詩晴Python網頁20260409</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=wanxun>傳送使用者暱稱</a><br>"
    homepage += "<a href=/account>網頁表單傳值</a><br>"
    homepage += "<a href=/about>洪詩晴簡介網頁</a><br>"
    homepage += "<a href=/calculator>次方與根號計算</a><br>"
    homepage += "<br><a href=/read>讀取全部Firestore資料</a><br>"
    # 指向新的查詢輸入頁面
    homepage += "<a href=/read2> 搜尋老師姓名關鍵字</a><br>"
    homepage += "<br><a href=/spider1>爬取子青老師本學期課程</a><br>"
    return homepage

# [其他原本的路由如 /mis, /today, /about, /welcome 等請保留...]

# --- 新增/修改的查詢功能 ---

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
    # 取得使用者輸入的關鍵字
    keyword = request.values.get("keyword", "").strip()
    if not keyword:
        return "您沒有輸入關鍵字！<br><a href='/read2'>重新查詢</a>"

    db = firestore.client()
    # 注意：這裡要確認你的集合名稱是 "資管二B2026" 還是 "靜宜資管"
    collection_ref = db.collection("資管二B2026")
    docs = collection_ref.get()

    found_count = 0
    table_html = f"""
    <h3>關於「{keyword}」的搜尋結果：</h3>
    <style>
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #2196f3; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #e1f5fe; }}
    </style>
    <table>
        <tr>
            <th>老師姓名</th>
            <th>詳細資料</th>
        </tr>
    """

    for doc in docs:
        teacher = doc.to_dict()
        # 搜尋邏輯：判斷關鍵字是否在姓名中
        if keyword in teacher.get("name", ""):
            found_count += 1
            table_html += f"<tr><td><strong>{teacher.get('name')}</strong></td><td>{str(teacher)}</td></tr>"

    table_html += "</table>"

    if found_count == 0:
        return f"查無姓名包含「{keyword}」的老師資料。<br><br><a href='/read2'>重新查詢</a> | <a href='/'>返回首頁</a>"

    return table_html + f"<br><p>共找到 {found_count} 筆資料</p><a href='/read2'>再次查詢</a> | <a href='/'>返回首頁</a>"

# [原本的 /spider1 路由...]
@app.route("/spider1")
def spider():
    R = ""   
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    try:
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".team-box a")
        for i in result:
            R += i.text + " ( " + i.get("href") + " )" + "<br>"
    except Exception as e:
        R = "爬蟲出錯: " + str(e)
    return R

if __name__ == "__main__":
    app.run(debug=True)