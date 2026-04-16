from flask import Flask, render_template, request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
	homepage = "<h1>洪詩晴Python網頁20260409</h1>"
	homepage += "<a href=/mis>MIS</a><br>"
	homepage += "<a href=/today>顯示日期時間</a><br>"
	homepage += "<a href=/welcome?nick=wanxun>傳送使用者暱稱</a><br>"
	homepage += "<a href=/account>網頁表單傳值</a><br>"
	homepage += "<a href=/about>洪詩晴簡介網頁</a><br>"
	homepage +="<a href=/calculator>次方與根號計算</a><br>"
	homepage += "<br><a href=/read>讀取Firestore資料</a><br>"
    homepage += "<br><a href=/read>讀取Firestore資料(根據姓名關鍵字:楊)</a><br>"
	return homepage


@app.route("/mis")
def course():
	return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
	now = datetime.now()
	return render_template("today.html",datetime = str(now))

@app.route("/about")
def me():
	return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("nick")
    d = request.values.get("d")
    c= request.values.get("c")
    return render_template("welcome.html", name=user,dep = d,course = c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")


@app.route("/calculator")
def calculator():
    return render_template("calculator.html")

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("資管二B2026")    
    docs = collection_ref.order_by("lab",direction=firestore.Query.DESCENDING).get()    
    for doc in docs:         
        Result += str(doc.to_dict()) + "<br>"    
    return Result
@app.route("/read2")
  Result = ""
  keyword="楊"
    db = firestore.client()
    collection_ref = db.collection("資管二B2026")    
    docs = collection_ref.get()    
    for doc in docs: 
        teacher=doc.to_dict()
        if keyword in teacher["name"]:        
        Result += str(teacher) + "<br>"

    if Result=="":
           Result="抱歉,查無此姓名資料" 
    return Result


if __name__ == "__main__":
	app.run(debug=True)