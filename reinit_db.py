import sqlite3, os

if os.path.exists("sites.db"): os.remove("sites.db")

sql = sqlite3.connect("sites.db")
sql.execute("create table sites (url varchar(255), title varchar(255), description varchar(255));")