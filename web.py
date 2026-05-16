import math
import os
import json

from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

import requests
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>C-C-Yang個人首頁2026/04/09</h1>"
    link += "<a href=/today>目前時間</a><hr>"
    link += "<a href=/cy>誠摯地自介</a><hr>"
    link += "<a href=/wc?u=Panco&d=靜宜大學&c=資訊管理導論>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/calc>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/read2>讀取Firestore資料(根據姓名關鍵字)</a><hr>"
    link += "<a href=/spider>爬取子青老師本學期課程</a><hr>"
    link += "<a href=/search>教師查詢</a><hr>"
    link += "<a href=/movie1>查詢即將上映電影</a><hr>"
    link += "<a href=/spidermovie>爬取即將上映電影到資料庫</a><hr>"
    link += "<a href=/searchMovie>從資料庫查詢即將上映電影</a><hr>"
    link += "<a href=/road>台中市十大肇事路口</a><hr>"
    link += "<a href=/weather>台灣各縣市天氣預報</a><hr>"
    link += "<a href=/rate>爬取本周新片含分級</a><hr>"
    return link

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    #msg =  req["queryResult"]["queryText"]
    #info = "我是楊承智設計的機器人,動作：" + action + "； 查詢內容：" + msg

    if (action == "rateChoice"):
        rate = req["queryResult"]["parameters"]["rate"]
        info = "我是楊承智開發的電影聊天機器人,您選擇的電影分級是：" + rate
        db = firestore.client()
        collection_ref = db.collection("本週新片含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

# ── Bug 1 修正：移除重複的 index()，改用 render_template 引用 weather.html ──

@app.route("/weather")
def weather():
    city = request.args.get("city", "").strip()
    city = city.replace("台", "臺")

    if not city:
        return render_template("weather.html", city="", weather=None, rain=None, location=None, error=None)

    url = (
        "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        "?Authorization=rdec-key-123-45678-011121314"
        "&format=JSON"
        "&locationName=" + city
    )

    try:
        Data = requests.get(url, timeout=10, verify=False)
        JsonData = json.loads(Data.text)
        location_data = JsonData["records"]["location"][0]

        location = location_data["locationName"]
        weather_val = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        rain = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]

        return render_template(
            "weather.html",
            city=city,
            location=location,
            weather=weather_val,
            rain=rain,
            error=None
        )

    except (KeyError, IndexError):
        return render_template("weather.html", city=city, weather=None, rain=None, location=None, error="找不到該縣市，請確認名稱是否正確（例如：臺北市、高雄市）")
    except Exception as e:
        return render_template("weather.html", city=city, weather=None, rain=None, location=None, error=f"查詢失敗：{str(e)}")

# ── Bug 2 修正：以下 route 全部移到 if __name__ 之前 ──

@app.route("/road")
def road():
    R = "<h1>台中市十大肇事路口(113年10月)-楊承智做的</h1><br>"
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        Data = requests.get(url, headers=headers, timeout=10, verify=False)
        JsonData = Data.json()
    except Exception as e:
        return f"<h1>抓取失敗</h1><p>{e}</p><pre>{Data.text[:500] if 'Data' in dir() else ''}</pre>"

    for item in JsonData:
        R += f"{item['路口名稱']} 原因:{item['主要肇因']} 共 {item['總件數']} 件<br>"
    return R

@app.route("/searchMovie")
def searchMovie():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return render_template("searchMovie.html")

    db = firestore.client()
    docs = db.collection("電影2B").stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        if keyword in data.get("title", ""):
            results.append({
                "id": doc.id,
                "title": data.get("title", ""),
                "picture": data.get("picture", ""),
                "hyperlink": data.get("hyperlink", ""),
                "showDate": data.get("showDate", ""),
                "lastUpdate": data.get("lastUpdate", "")
            })

    if not results:
        return f"找不到包含「{keyword}」的電影。"

    R = f'''
        <h1>查詢電影&nbsp;</h1>
        <form action="/movie1" method="get">
            <input type="text" name="keyword" placeholder="請輸入電影關鍵字">
            <input type="submit" value="搜尋">
        </form>
        '''
    for idx, movie in enumerate(results, start=1):
        R += f"""
        <div style="margin-bottom:20px; border-bottom:1px solid #ccc; padding-bottom:10px;">
            <p><strong>編號：</strong>{idx}</p>
            <p><strong>片名：</strong>{movie['title']}</p>
            <img src="{movie['picture']}" alt="{movie['title']}" width="120"><br>
            <p><strong>海報連結：</strong><a href="{movie['picture']}" target="_blank">{movie['picture']}</a></p>
            <p><strong>上映日期：</strong>{movie['showDate']}</p>
            <p><strong>最新更新日期：</strong>{movie['lastUpdate']}</p>
            <p><a href="{movie['hyperlink']}" target="_blank">➜ 介紹頁</a></p><br>
            <a href=/>返回個人首頁</a><br>
        </div>
        """
    return R

@app.route("/spidermovie")
def spidermovie():
    R = ""
    db = firestore.client()

    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="grey").text.replace("更新時間：", "")

    result = sp.select(".filmListAllX li")
    total = 0
    for item in result:
        total += 1
        movie_id = item.find("a").get("href").replace("/movie/", "").replace("/", "")
        tittle = item.find(class_="filmtitle").text
        picture = "https://www.atmovies.com.tw/" + item.find("img").get("src")
        hyperlink = "https://www.atmovies.com.tw/" + item.find("a").get("href")
        showDate = item.find(class_="runtime").text[0:15]

        doc = {
            "title": tittle,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "lastUpdate": lastUpdate
        }

        doc_ref = db.collection("電影2B").document(movie_id)
        doc_ref.set(doc)
    R += "更新日期:" + lastUpdate + '<br>'
    R += "總共爬取" + str(total) + "部電影" + '<br>'
    return R

@app.route("/movie1")
def movie1():
    keyword = request.args.get("keyword", "")

    if not keyword:
        return render_template("movie.html")

    try:
        R = ""
        url = "https://www.atmovies.com.tw/movie/next/"
        Data = requests.get(url, timeout=10)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".filmListAllX li")
        for item in result:
            name = item.find("img").get("alt")
            href = "https://www.atmovies.com.tw" + item.find("a").get("href")
            src  = "https://www.atmovies.com.tw" + item.find("img").get("src")
            if keyword in name:
                R += f'<a href="{href}">{name}</a><br>'
                R += f'<img src="{src}"><br><br>'

        if not R:
            R = f"找不到包含「{keyword}」的電影<br><br>"

        return render_template("movie.html", result=R, keyword=keyword)

    except Exception as e:
        return f"錯誤原因：{str(e)}"

@app.route("/search", methods=["GET"])
def searrch():
    keyword = request.args.get("keyword", "")
    results = []

    if keyword:
        db = firestore.client()
        teachers = db.collection("靜宜資管").stream()
        for teacher in teachers:
            data = teacher.to_dict()
            if keyword in data.get("name", ""):
                results.append(data)

    return render_template("search.html", keyword=keyword, results=results)

@app.route("/spider")
def spider():
    R = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url, verify=False)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".team-box a")
    for i in result:
        R += i.text + i.get("href") + "<br>"
    return R

@app.route("/read2")
def read2():
    Result = ""
    keyword = "楊"
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.get()
    for doc in docs:
        teacher = doc.to_dict()
        if keyword in teacher["name"]:
            Result += str(teacher) + "<br>"
    if Result == "":
        Result = "抱歉，查無此關鍵字姓名枝老師資料"
    return Result

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.get()
    for doc in docs:
        Result += str(doc.to_dict()) + "<br>"
    return Result

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))

@app.route("/cy")
def cy():
    return render_template("about.html")

@app.route("/wc", methods=["Get"])
def wc():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name=user, dep=d, course=c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd
        return result
    else:
        return render_template("account.html")

@app.route("/calc", methods=["GET", "POST"])
def calc():
    if request.method == "POST":
        x = int(request.form["x"])
        op = request.form["op"]
        y = int(request.form["y"])
        ans = 0
        if op == "power":
            ans = x ** y
        elif op == "sqrt":
            if y == 0:
                ans = "他媽數學白癡,y不能為0"
            else:
                ans = x ** (1/y)
        return render_template("calculate.html", result=ans)
    else:
        return render_template("calculate.html", result=None)

if __name__ == "__main__":
    app.run(debug=True)