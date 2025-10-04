import sqlite3

# データベースファイルに接続, 存在しない場合は新しく作成されます
conn = sqlite3.connect("datafile.db")
# SQL文を実行するためのカーソルオブジェクトを作成 
cursor = conn.cursor()

# テーブル1: cash
cursor.execute(
    """create table cash (transaction_id integer primary key, 
                          taiwanese_dollars integer, 
                          us_dollars real, note varchar(30), 
                          date_info date)""")
# テーブル2: stock
cursor.execute(
    """create table stock (transaction_id integer primary key,  
                           stock_id varchar(10), 
                           stock_num integer,
                           stock_price real, 
                           processing_fee integer, 
                           tax integer, 
                           date_info date)""")

# データベースに変更を保存する
conn.commit()
conn.close()
