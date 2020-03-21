import time
import os
#import urllib.parse as urlparse
import psycopg2

from Camera import Camera
from Viewer import Viewer

# DB
#url = urlparse.urlparse(os.environ['DATABASE_URL'])
#dbname = url.path[1:]
#user = url.username
#password = url.password
#host = url.hostname
#port = url.port

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
con.close()

# main observe loop
while(True):
    observations = []
    for camera in cameras[:3]:
        v = Viewer(camera)
        o = v.createObservation()
        if (o is not None):
            observations.append(o)

    sql = "INSERT INTO observations (id, camera_id, count) VALUES "
    for observation in observations:
        sql += "('%s', '%s', '%s'), " %(observation.id, observation.cameraId, observation.count)

    sql = sql[:-2]
    
    cur2 = con.cursor()
    cur2.execute(sql)
    con.commit()
    cur2.close()
    con.close()
    time.sleep(120)
