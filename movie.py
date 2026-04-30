import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

import requests
from bs4 import BeautifulSoup
url = "http://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")
lastUpdate = sp.find(class_="smaller09").text.replace("更新時間 : ", "").strip()

result = sp.select(".filmListAllX li")
info = ""
total = 0  # 修正：統一使用 total

for item in result:
    total += 1
    movie_id = item.find("a").get("href").replace("/movie/", "").replace("/", "")
    title = item.find(class_="filmtitle").text
    picture = "https://www.atmovies.com.tw" + item.find("img").get("src")
    hyperlink = "https://www.atmovies.com.tw" + item.find("a").get("href")
    
    # 抓取上映日期
    showDate = item.find(class_="runtime").text[5:15]

    # 抓取片長資訊 (縮排已修正，確保在迴圈內)
    try:
        showLength = item.find(class_="runtime").text.split("片長：")[1].strip()
    except:
        showLength = "未知"

    info += movie_id + "\n" + title + "\n"
    info += picture + "\n" + hyperlink + "\n" + showDate + "\n\n"

    # 建立資料字典 (縮排已修正，確保每跑一次迴圈就寫入一筆資料)
    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
    }

    # 寫入 Firestore
    doc_ref = db.collection("電影2B").document(movie_id)
    doc_ref.set(doc)

# 迴圈結束後印出結果
print(lastUpdate)
print("總共爬取 " + str(total) + " 部電影到資料庫") # 修正：這裡的 total 必須跟上面定義的一樣