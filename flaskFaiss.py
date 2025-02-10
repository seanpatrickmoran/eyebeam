import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)


 
from flask import Flask, jsonify
from flask import request
# from flaskTouch.py import getRowId
# from .flaskTouch import getRowId

import sqlite3
import ollama
import faiss
import numpy as np
from typing import List
import struct
import datetime


dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"
dbSQLITE3VEC = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/VIRT5_SQLITE_databaseVEC.db"


def call(PATH,TIMEOUT):
    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor


def deserialize_f32(vector,size=256):
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.unpack(f"{size}f", vector)


def getEverything(dbPATH, timeout=10):
    connection,cursor=call(dbPATH,timeout)
    try:
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT rowid,embedding from vector_table")
        print(f"success")
        reply = [(a,deserialize_f32(b)) for a,b in cursor.fetchall()]
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
    return reply

if __name__ == "__main__":
    app = Flask(__name__)
    index = faiss.read_index("/Users/seanmoran/Projects/pyBeam/eyeBeam/faiss.test.index")
    assert index.is_trained

    rows = getEverything(dbSQLITE3VEC);
    ### faiss here.
    k=50
    d = 256                           # dimension
    nb = len(rows)                      # database size
    nq = nb//10                       # nb of queries
    xb=np.array([np.array(xi[1]) for xi in rows]).astype('float32')
    print(xb.shape)
    # xb[:, 0] += np.arange(nb) / 1000.


 
@app.route("/test", methods=['GET'])
def hello_microservice():
    message = {"message": "meow! @ flask"}
    return jsonify(message)
 

 
@app.route("/test2", methods=['GET'])
def checkDB():
    name = request.args.get('name', default = "", type = str)
    nArr = nameToNArr(dbSOURCE, name, 10);
    query = ollama.embed(model='llama3.2', input=str(nArr),)

    # print(query.embeddings[0])
    xq = np.array([np.array(xi[0:256]) for xi in query.embeddings])

    # print(xq)
    # xq[:, 0] += np.arange(1) / 1000.
    D, I = index.search(xb, k) # sanity check

    print(I)
    print()
    message = {"message":[]}

    for node in I[0]:
        print(node)
        # node = rows.pop()
        val = rowIdToName(dbSOURCE, str(node+1), 10)
        if val != [0]:
            message["message"]+=[val]

    return jsonify(message)
 








def call(PATH,TIMEOUT):
    #only for SOURCE db
    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor


def nameToNArr(dbPATH=dbSOURCE, name="", timeout=10):
    if name=="":
        return
    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
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



def rowIdToName(dbPATH=dbSOURCE, rowID="", timeout=10):
    if rowID=="":
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        print(rowID, type(rowID))
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
