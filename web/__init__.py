from flask import Flask, jsonify
import os
#import urllib.parse as urlparse
import psycopg2

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/observations', methods=['GET'])
def observations():
    con = _getDbConnection()
    cur = con.cursor()
    cur.execute("SELECT observations.id, observations.camera_id, observations.count, observations.date, cameras.long, cameras.lat FROM observations INNER JOIN cameras ON observations.camera_id=cameras.camera_id")
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
    return jsonify({'observations': obs})

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