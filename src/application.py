from flask import Flask
from decimal import Decimal
import os
import simplejson
import psycopg2
import psycopg2.extras

app = Flask(__name__)
try:
  conn = psycopg2.connect("dbname='RawData' user='donorschoose' host='db.hack' password='7E*ni7WoUBo*'")
except:
  print "Cannot connect!!!"

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def json_query(query):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query)
    rows = cur.fetchall()
    return simplejson.dumps(rows,default=date_handler)

@app.route("/")
def hello():
    return json_query("""SELECT * from normalized_project limit 10""")

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
