import time
import os
import urllib.parse as urlparse
import psycopg2

from Camera import Camera
from Viewer import Viewer

# DB
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
cur = con.cursor()

# get cameras
cur.execute("SELECT camera_id, ip FROM cameras")

cameras = []
for row in cur.fetchall():
    cameras.append(Camera(row[0], row[1]))

cur.close()

# main observe loop
while(True):
    observations = []
    for camera in cameras:
        v = Viewer(camera)
        o = v.createObservation()
        if (o is not None):
            observations.append(o)

    sql = "INSERT INTO observations (id, camera_id, date, count) VALUES (%s, %s, %s, %s)"
    sql_vals = []
    for observation in observations:
        sql_vals.append((observation.id, observation.cameraId, observation.date, observation.count))

    cur2 = con.cursor()
    cur2.executemany(sql, sql_vals)
    con.commit()
    time.sleep(120)
