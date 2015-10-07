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

def json_query(query,params={}):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query,params)
    rows = cur.fetchall()
    return simplejson.dumps(rows,default=date_handler)

@app.route("/")
def hello():
    return json_query("""SELECT * from normalized_project limit 10""")

@app.route("/donations")
def donations_by_state():
    return json_query("""select 
    school_state,
    primary_focus_area,
    total_donations,
    rank() over (partition by primary_focus_area order by total_donations desc) 
from (
    select 
        school_state,
        primary_focus_area,
        sum(total_donations) as total_donations 
    from 
        donorschoose_projects 
    group by 1,2
    ) foo order by 2,4;""")

@app.route("/detail/<state>")
def state_detail(state):
    return json_query("select * from yeswecode_total_donation_state_year1 where school_state=%(state)s",{'state':state});

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
