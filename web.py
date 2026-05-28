import requests
import json
import os
import urllib3
from flask import Flask, request, make_response, jsonify, render_template
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from bs4 import BeautifulSoup
from google import genai
from google.genai import types


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
client = genai.Client()


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
    homepage += "<a href='/webhook7'>聊天機器人</a><br>"
    homepage += "<a href='/AI'>AI進行測試</a><br>"
    homepage += "<a href='/ask'>ask</a><br>"
    return homepage

@app.route('/ask', methods=['GET', 'POST']) 
def ask():
    if request.method == "POST":
        user_prompt = request.form.get('prompt', '')
        if not user_prompt:
            return "請輸入內容", 400
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=user_prompt,
            )
            return response.text
        except Exception as e:
            return f"發生錯誤: {str(e)}", 500
    else:    
        return render_template("ask.html")


@app.route("/AI")
def AI():
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents='我想查詢靜宜大學資管系的評價？',
    )
    return response.text

@app.route("/webhook7", methods=["GET"])
def demo():
    return render_template("demo.html")

@app.route("/webhook7", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    
    # 按照投影片第 11 行的安全寫法擷取 action
    action = req.get("queryResult").get("action")
    
    # 1. 處理電影分級查詢
    if (action == "rateChoice"):
        rate = req["queryResult"]["parameters"]["rate"]
        
        db = firestore.client()
        collection_ref = db.collection("本週新片含分級B")
        docs = collection_ref.where("rate", "==", rate).get()
        
        if not docs:
            info = f"目前資料庫中沒有找到分級為「{rate}」的本週新片喔！"
        else:
            info = f"我是洪詩晴設計的機器人，為您推薦本週的{rate}電影：\n"
            for doc in docs:
                movie_data = doc.to_dict()
                title = movie_data.get("title")
                link = movie_data.get("hyperlink")
                info += f"🎬 {title}\n連結：{link}\n\n"

    # 2. 處理 Fallback (對應投影片紅框，並整合 Gemini 智慧助理)
    elif (action == "input.unknown"):
        instruction_text = (
            "你是一個熱心且知識豐富的專業智慧助理。"
            "對於使用者的提問，請回覆重點的關鍵字，不要重述問題。"         
        )

        ai_config = types.GenerateContentConfig(
            max_output_tokens=500, 
            system_instruction=instruction_text
        )
        
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite', 
                contents=req["queryResult"]["queryText"],
                config=ai_config,
            )

            if response.text:
                info = response.text
            else:
                info = "抱歉，我現在無法生成回應，請稍後再試。"
        except Exception