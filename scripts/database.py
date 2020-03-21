import psycopg2
from configparser import ConfigParser
import crawler 

def config(filename='database.ini', section='postgresql'):
  parser = ConfigParser()
  parser.read(filename)

  # get section, default to postgresql
  db = {}
  if parser.has_section(section):
    params = parser.items(section)
    for param in params:
      db[param[0]] = param[1]
  else:
    raise Exception(
      "Section {0} not found in the {1} file".format(section, filename))

  return db

def create_tables():
  conn = None
  sql = """
        CREATE TABLE cameras (
            camera_id SERIAL PRIMARY KEY,
            ip VARCHAR(255) NOT NULL,
            loc VARCHAR(255),
            lat VARCHAR(255),
            long VARCHAR(255)
        )
        """
  try:
    params = config()
    print("Connecting to the PostgreSQL database...")
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(sql)

    cur.close()
    conn.commit()
  except(Exception) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
      print("Database connection closed.")

def fill_tables():
  conn = None
  try:
    params = config()
    conn = psycopg2.connect(**params)
    print("Filling PostgreSQL database")
    
    crawler.crawl(conn)

  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()
      print("Database connection closed.")