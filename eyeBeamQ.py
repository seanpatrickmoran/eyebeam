#testfire

import sqlite3
import sqlite_vec
import ollama
from typing import List
import struct
import datetime

def call(PATH,TIMEOUT):

    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor




def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)

try:
  dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"
  db = sqlite3.connect(dbVECTOR)
  db.enable_load_extension(True)
  sqlite_vec.load(db)
  db.enable_load_extension(False)

  dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
  connection_s,cursor_s=call(dbSOURCE,10)
  cursor_s.row_factory = sqlite3.Row
  cursor_s.execute("SELECT rowid, * FROM imag LIMIT ? OFFSET ?", (1,12))
  reply = []
  for en in cursor_s.fetchall():
      reply = str(en[5])


  query = ollama.embed(model='llama3.2', input=reply, options={'num_gpus': 99})


  print(query.embeddings[0])
  print(len(query.embeddings[0]))


  rows = db.execute(
      """
        SELECT
          rowid,
          distance
        FROM vec_items
        WHERE embedding MATCH ?
        AND k = 3
      """,
    [serialize_f32(query.embeddings[0][:256])],
  ).fetchall()
  print(rows)


except Exception as e:
    print(e)

finally:
    db.close()


#(13, 0.0), (1830, 0.04230758175253868), (350, 0.05124296247959137)]


#rank here...
#https://github.com/nmslib/hnswlib


#rerank this.
#https://github.com/asg017/sqlite-vec