from flask import Flask, render_template, request
from flask_socketio import SocketIO
import sqlite3 as sql
import re

con = sql.connect("sites.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search/")
def search():
    query = request.args.get("q")
    tbl = "title"
    if "[SEARCH-URL]" in query:
        query = query.replace("[SEARCH-URL]", "")
        tbl = "url"
    elif "[SEARCH-DESCRIPTION]" in query:
        query = query.replace("[SEARCH-DESCRIPTION]", "")
        tbl = "description"
    page = request.args.get("page")
    #do indexing
    results = {}
    cmd = f"select * from sites where {tbl} like '%{query}%' limit 20"
    if not page in [None, ""]: cmd += " offset " + str(int(page) * 20)
    num_results_lst = con.execute("select * from sites where title like '%" + query + "%'")
    num_results = 0
    for dgfdsf in num_results_lst: num_results += 1
    for result in con.execute(cmd):
        url = result[0]
        title = result[1]
        description = result[2]
        display_url = url.split("?")[0]
        display_url = display_url[1:] if display_url[0] == "/" else display_url
        results[title] = {"display_url": display_url, "url": url, "description": description}
    return render_template("results.html", search_term=query, results=results, found=True if len(results) > 0 else False, num_results=num_results)

if __name__ == '__main__':
    sio.run(app, "0.0.0.0", "80")