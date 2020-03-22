from flask import Flask, jsonify, request
import os
import urllib.parse as urlparse
import psycopg2
import time

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/observations', methods=['GET'])
def observations():
    con = _getDbConnection()
    cur = con.cursor()
    if request.args:
        args = request.args
        date_from = time.ctime(float(args["from"]))
        date_to = time.ctime(float(args["to"]))
        cur.execute("""
        SELECT observations.id, observations.camera_id, observations.count, observations.date, cameras.long, cameras.lat
        FROM observations
        INNER JOIN cameras
        ON observations.camera_id=cameras.camera_id
        WHERE observations.date >= (%s)::date
        AND observations.date <= (%s)::date
        """, (date_from, date_to))
    else:
        cur.execute("""
        SELECT observations.id, observations.camera_id, observations.count, observations.date, cameras.long, cameras.lat
        FROM observations
        INNER JOIN cameras
        ON observations.camera_id=cameras.camera_id""")
    obs = []
    for row in cur.fetchall():
        obs.append({
            'id': row[0],
            'camera_id': row[1],
            'count': row[2],
            'date': row[3],
            'long': row[4],
            'lat': row[5],
        })
    cur.close()
    con.close()
    return jsonify({'observations': obs})

@app.route('/restrictions', methods=['GET'])
def restrictions():
    con = _getDbConnection()
    cur = con.cursor()
    if request.args:
        args = request.args
        state = args["state"]
        sql = "SELECT * FROM warnings WHERE region=(%s)"
        cur.execute(sql, (state, ))
        result = cur.fetchall()[0];
        cur.close()
        con.close()
        return jsonify({
            'region': result[0],
            'cases': result[1],
            'deaths': result[4],
            'per100k': result[5],
            'level': result[2],
            'start': result[3]
        })
    else:
        cur.execute("SELECT * FROM warnings")
        results = cur.fetchall()
        cur.close()
        con.close()
        all_regions = []
        for result in results:
            all_regions.append({
                'region': result[0],
                'cases': result[1],
                'deaths': result[4],
                'per100k': result[5],
                'level': result[2],
                'start': result[3]
            })
        return jsonify(all_regions)

def _getDbConnection():
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    con = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
                )
    return con