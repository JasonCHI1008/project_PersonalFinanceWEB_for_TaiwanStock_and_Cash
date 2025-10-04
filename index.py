from flask import Flask, render_template, request, g, redirect
import sqlite3
import requests
import math
import matplotlib.pyplot as plt
import matplotlib
import os
matplotlib.use("agg")

# Flask アプリケーションの「本体」を作成しています
app = Flask(__name__)
database = "datafile.db"

BASE_DIR = app.root_path  # プロジェクトのルートパス
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)  # staticフォルダが無ければ作る
def init_db():
    # g を使わず、直接接続してテーブル作成するのが安全
    with sqlite3.connect(database) as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS cash(
            transaction_id INTEGER PRIMARY KEY,
            taiwanese_dollars INTEGER,
            us_dollars REAL,
            note VARCHAR(30),
            date_info DATE
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS stock(
            transaction_id INTEGER PRIMARY KEY,
            stock_id VARCHAR(10),
            stock_num INTEGER,
            stock_price REAL,
            processing_fee INTEGER,
            tax INTEGER,
            date_info DATE
        )""")
        conn.commit()

# ← app を作った直後あたりで一度だけ実行
with app.app_context():
    init_db()

# Flaskアプリケーション内で、SQLiteデータベースへの接続を管理する処理
def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = sqlite3.connect(database)
    return g.sqlite_db

# Flask アプリケーションで使われた SQLite データベース接続を、リクエスト終了時に自動的に閉じるための処理
@app.teardown_appcontext
def close_connection(exception):
    print("我們正在關閉sql connection....")
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

# connect to html pages
@app.route("/")
def home():
    # get data info from database
    conn = get_db()
    cursor = conn.cursor()
    result = cursor.execute("select * from cash")
    cash_result = result.fetchall()
     # calculate sum of taiwanese dollars and us dollars
    taiwanese_dollars = 0
    us_dollars = 0
    for data in cash_result:
        taiwanese_dollars += data[1]
        us_dollars += data[2]
    # get exchange rate
    r=requests.get('https://tw.rter.info/capi.php')
    currency=r.json()
    total = math.floor(taiwanese_dollars + us_dollars * currency["USDTWD"]["Exrate"])
    
    # get stock info
    result2 = cursor.execute("select * from stock where stock_id")
    stock_result = result2.fetchall()
    # find unique stock id
    unique_stock_list = []
    for data in stock_result:
        if data[1] not in unique_stock_list:
            unique_stock_list.append(data[1])
    # calculate sum of stock value                                  
    total_stock_value = 0
    stock_info = []
    for stock in unique_stock_list:
        result = cursor.execute("select * from stock where stock_id =?", (stock,))
        result = result.fetchall()
        stock_cost = 0 # 總花費
        shares = 0 # 持股數
        for d in result:
            shares += d[2]
            stock_cost += d[2] * d[3] + d[4] + d[5]
            stock_cost = round(stock_cost)
        # get current stock price
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo=" + stock
        response = requests.get(url)
        data = response.json()
        price_list = data["data"]
        # 目前股價
        # remove , if price is over 1,000
        current_price = float(price_list[ len(price_list) - 1][6].replace(',', ''))
        # 目前市值
        total_value = int(current_price * shares)
        # 加到全部股票的市值        
        total_stock_value += total_value
        # 平均成本
        average_cost = round(stock_cost/shares, 2)
        # 報酬率
        roe =round((total_value - stock_cost) * 100 / stock_cost, 2) 
        stock_info.append({"stock_id":stock, "stock_cost": stock_cost, "total_value":total_value,
                            "average_cost":average_cost, "shares": shares, "current price" : current_price, "ROE":roe})
    # 每股票市值佔總體多少
    for stock in stock_info:
        stock["value_percentage"] = round(stock["total_value"]*100/total_stock_value,2)
    
    # plot the pie chart of stock
    if len(unique_stock_list) != 0:
        labels = tuple(unique_stock_list)
        sizes = [d["total_value"] for d in stock_info]
        fig, ax = plt.subplots(figsize=(6,5))
        ax.pie(sizes, labels=labels, autopct=None, shadow=None)
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0,hspace=0, wspace=0)
        

        pie1_path = os.path.join(STATIC_DIR, "piechart.jpg")
        plt.savefig(pie1_path, dpi=200)
        plt.close(fig)  # 忘れずに閉じる
    else:
        try:
            pie1_path = os.path.join(STATIC_DIR, "piechart.jpg")
            if os.path.exists(pie1_path):
                os.remove(pie1_path)
        except:
            pass
    # plot the pie chart of stock and cash
    if us_dollars != 0 or taiwanese_dollars != 0 or total_stock_value != 0:
        labels = ("USD", "NTD", "Stock")
        sizes = (us_dollars * currency["USDTWD"]["Exrate"], taiwanese_dollars, total_stock_value)
        fig, ax = plt.subplots(figsize=(6,5))
        ax.pie(sizes, labels=labels, autopct=None, shadow=None)
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0,hspace=0, wspace=0)
        

        pie2_path = os.path.join(STATIC_DIR, "piechart2.jpg")
        plt.savefig(pie2_path, dpi=200)
        plt.close(fig)
    else:
        try:
            pie2_path = os.path.join(STATIC_DIR, "piechart2.jpg")
            if os.path.exists(pie2_path):
                os.remove(pie2_path)
        except:
            pass
    
    data = {"show_pic_1":os.path.exists("static/piechart.jpg"),
            "show_pic_2":os.path.exists("static/piechart2.jpg"),
            "total":total, "currency":currency["USDTWD"]["Exrate"], "usd":us_dollars, "ntd":taiwanese_dollars,
            "cash_result":cash_result, "stock_info":stock_info }


    return render_template("index.html", data = data)

@app.route("/cash")
def cash():
    return render_template("cash.html")

@app.route("/cash", methods=["POST"]) #對伺服器提交資料
def submit_cash():
    # get data from page form
    taiwanese_dollars = 0
    us_dollars = 0
    if request.values["taiwanese-dollars"] != "":
        taiwanese_dollars = request.values["taiwanese-dollars"]
    if request.values["us-dollars"] != "":
        us_dollars = request.values["us-dollars"]
    note = request.values["note"]
    date = request.values["date"]

    # update database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""insert into cash (taiwanese_dollars, us_dollars, note, date_info) values (?,?,?,?)""",
                   (taiwanese_dollars, us_dollars,note, date))
    conn.commit()

    # return homepage
    return redirect("/")

    return "感謝提交表單。。。"

@app.route("/cash-delete", methods=["POST"])
def delete_cash():
    transaction_id = request.values["id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""delete from cash where transaction_id=?""",(transaction_id, ) )
    conn.commit()

    return redirect("/")

@app.route("/stock")
def stock():
    return render_template("stock.html")

@app.route("/stock", methods=["POST"])
def submit_stock():
    # get data from page form
    stock_id = request.values["stock-id"]
    stock_num = request.values["stock-num"]
    stock_price = request.values["stock-price"]
    stock_fee = 0
    tax = 0
    if request.values["stock-fee"] != "":
        stock_fee = request.values["stock-fee"]
    if request.values["tax"] != "":
        tax = request.values["tax"]
    date = request.values["date"]
    
    # update data in database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""insert into stock (stock_id, stock_num, stock_price, processing_fee, tax, date_info) values (?,?,?,?,?,?)""",
                   (stock_id,stock_num,stock_price, stock_fee, tax, date))
    conn.commit()

    # return homepage
    return redirect("/")

    return "感謝提交表單。。。"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)