from flask import Flask, render_template,request
from datetime import datetime
import math
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
    link = "<h1>C-C-Yang個人首頁2026/04/09</h1>"
    link += "<a href=/today>目前時間</a><hr>"
    link += "<a href=/cy>誠摯地自介</a><hr>"
    link += "<a href=/wc?u=Panco&d=靜宜大學&c=資訊管理導論>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/calc>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    return link
    
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
    return render_template("today.html", datetime = str(now))

@app.route("/cy")
def cy():
    return render_template("about.html")

@app.route("/wc", methods = ["Get"])
def wc():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name = user, dep = d, course = c)

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
        return render_template("calculate.html", result = ans)
    else:
        return render_template("calculate.html", result = None)
if __name__ == "__main__":
    app.run(debug=True)