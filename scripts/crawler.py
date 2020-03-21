from bs4 import BeautifulSoup
import urllib.request
import re
import psycopg2

header = {"User-Agent": "Mozilla/5.0"}
ip_regex = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b\:\d*"
insert_sql = """INSERT INTO cameras (camera_id, ip, loc, lat, long)
             VALUES(%s, %s, %s, %s, %s)"""

def crawl(conn):
  cur = conn.cursor()
  for page_num in range(1, 101):
    URL = f"https://www.insecam.org/en/bycountry/DE/?page={page_num}"
    try:
      curr_page = urllib.request.Request(URL, headers=header)
      res = urllib.request.urlopen(curr_page)
      soup = BeautifulSoup(res, "html.parser")
      cam_list = soup.find_all("div", {"class", "thumbnail-item__preview"})

      for cam in cam_list:
        for info in cam.find_all(title=re.compile("Axis")):
          location = re.findall(r"(Germany.*)$", info["title"])[0]
          cam_id = info["id"][5:]
          ip = re.findall(ip_regex, info["src"])[0]
          lat_long = get_location(cam_id)
          insert_vals = (cam_id, ip, location, lat_long[0], lat_long[1])
          cur.execute(insert_sql, insert_vals)
          conn.commit()
    except Exception as error:
      print(error)
  cur.close()

def get_location(cam_id):
  URL = f"https://www.insecam.org/en/view/{cam_id}"
  try:
    curr_page = urllib.request.Request(URL, headers=header)
    res = urllib.request.urlopen(curr_page)
    soup = BeautifulSoup(res, "html.parser")
    info_list = soup.find_all("div", {"class", "camera-details__row"})
    lat = info_list[4].find_all("div", {"class", "camera-details__cell"})[1].text
    long = info_list[5].find_all(
        "div", {"class", "camera-details__cell"})[1].text
    return [lat.replace("\n", ""), long.rstrip().replace("\n", "")]
  except Exception as error:
    print(error)
