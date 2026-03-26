from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>洪詩晴的python網頁</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=tcyang>傳送使用者暱稱</a><br>"
    homepage += "<a href=/account>網頁表單傳值</a><br>"
    homepage += "<a href=/about>洪詩晴簡介網頁</a><br>"
    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now=datetime.now()
    return render_template("today.html",datetime=str(now))

@app.route("/me")
def me():
    return render_template("aboutme6.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d= request.values.get("d")
    c= request.values.get("c")
 
    return render_template("welcome.html", name=user,dep=d,course=c)
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")



if __name__ == "__main__":
    app.run(debug=True)
