import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)


 
from flask import Flask, jsonify
from flask import request
# from flaskTouch.py import getRowId
# from .flaskTouch import getRowId

import sqlite3
import sqlite_vec
import ollama
from typing import List
import struct
import datetime


def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)

dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"
app = Flask(__name__)
 
@app.route("/test", methods=['GET'])
def hello_microservice():
    message = {"message": "meow! @ flask"}
    return jsonify(message)
 
# @app.route("/apiv2/faiss_query", methods=['GET'])
# def hello_microservice():
#     message = {"message": "meow! @ flask"}
#     return jsonify(message)
 
# @app.route("/apiv1/sqlitevec_knn", methods=['GET'])
# def hello_microservice():
#     message = {"message": "meow! @ flask"}
#     return jsonify(message)
 
@app.route("/test2", methods=['GET'])
def checkDB():
    name = request.args.get('name', default = "", type = str)
    print(name)
    print("@@@")
    nArr = nameToNArr(dbSOURCE, name, 10);
    # rowId = nameToRowId(dbSOURCE, "GM12878_2000_mustache_#5", 10);
    # nArr = getRowId(dbSOURCE, "1", 10);
    query = ollama.embed(model='llama3.2', input=str(nArr),)

    db = sqlite3.connect(dbVECTOR)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    rows = db.execute(
      """
        SELECT
          rowid,
          distance
        FROM vec_items
        WHERE embedding MATCH ?
        AND k = 5
      """,
    [serialize_f32(query.embeddings[0][:256])],
    ).fetchall()
    # print([x[0] for x in rows])

    message = {"message":[]}

    while rows:
        node = rows.pop()
        val = rowIdToName(dbSOURCE, str(node[0]), 10)
        if val != [0]:
            message["message"]+=[val]



    return jsonify(message)
 








def call(PATH,TIMEOUT):
    #only for SOURCE db
    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor


def nameToNArr(dbPATH=dbSOURCE, name="", timeout=10):
# def nameToRowId(dbPATH=dbSOURCE, name="", timeout=10):
    print(name)
    if name=="":
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        print(name)
        cursor_s.execute("SELECT * FROM imag WHERE name = ?", (name,))
        # cursor_s.execute("SELECT * FROM imag WHERE rowid = ? LIMIT 1", rowID) 
        row = cursor_s.fetchone()
        cursor_s.close()
        connection_s.close()
        # print(row[4])
        # return row
        return row[4]

    except Exception as e:
        cursor_s.close()
        connection_s.close()
        print(e)
        return [0]



# def nameToRowId(dbPATH=dbSOURCE, name="", timeout=10):
#     print(name)
#     if name=="":
#         return

#     #Full DB, not VEC
#     connection_s,cursor_s=call(dbPATH,timeout)

#     try:
#         cursor_s.execute("SELECT * FROM imag WHERE name = ?", (name,))
#         # cursor_s.execute("SELECT * FROM imag WHERE rowid = ? LIMIT 1", rowID) 
#         row = cursor_s.fetchone()
#         cursor_s.close()
#         connection_s.close()
#         print(row)
#         # return row
#         return row["rowid"]

#     except Exception as e:
#         cursor_s.close()
#         connection_s.close()
#         print(e)
#         return [0]


# def getRowId(dbPATH=dbSOURCE, rowID="", timeout=10):
#     if rowID=="":
#         return

#     #Full DB, not VEC
#     connection_s,cursor_s=call(dbPATH,timeout)

#     try:
#         cursor_s.execute("SELECT * FROM imag WHERE rowid = ?", (rowID,))
#         # cursor_s.execute("SELECT * FROM imag WHERE rowid = ? LIMIT 1", rowID) 
#         row = cursor_s.fetchone()
#         cursor_s.close()
#         connection_s.close()
#         return row["numpyarr"]

#     except Exception as e:
#         cursor_s.close()
#         connection_s.close()
#         print(e)
#         return [0]

def rowIdToName(dbPATH=dbSOURCE, rowID="", timeout=10):
    if rowID=="":
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        cursor_s.execute("SELECT * FROM imag WHERE rowid = ?", (rowID,))
        # cursor_s.execute("SELECT * FROM imag WHERE rowid = ? LIMIT 1", rowID) 
        row = cursor_s.fetchone()
        # print(row)
        cursor_s.close()
        connection_s.close()
        return row[0]

    except Exception as e:
        cursor_s.close()
        connection_s.close()
        print(e)
        return [0]


if __name__ == "__main__":
    app.run(port=9999)
