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

@app.route("/heatmap")
def heatmap():
    return json_query("select * from yeswecode_project_lat_long limit 1000")

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

@app.route("/poverty/<state>")
def poverty(state):
    sql="""
select * from
(select 
    school_state, 
    poverty_level, 
    rank() over(partition by poverty_level order by count(distinct _schoolid) desc) as school_count
from donorschoose_projects group by 1,2) foo 
where school_state=%(state)s;
"""
    return json_query(sql,{'state':state});

@app.route("/detail/<state>")
def state_detail(state):
    sql = """
select * from
  (select school_state, primary_focus_area, 
    rank() over (partition by primary_focus_area order by sum(total_donations) desc) as donation_rank,
    rank() over (partition by primary_focus_area order by sum(total_price_including_optional_support) desc) as request_rank
  from donorschoose_projects group by school_state, primary_focus_area) foo 
  where school_state=%(state)s and primary_focus_area is not null
"""
    return json_query(sql,{'state':state});

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
