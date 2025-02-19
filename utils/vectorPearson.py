#testfire

import sqlite3
import sqlite_vec
# from ollama import embed
import ollama
from typing import List
import struct
import array
import datetime

import numpy as np

dbSOURCE = "/Users/seanmoran/Documents/Master/2025/Feb2025/database_TEST/database_17_bin.db"
# dbSOURCE = "/Users/seanmoran/Documents/Master/2025/Feb2025/database_TEST/database_14_bin.db"
dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/database_TEST/EB_databaseVEC_14.db"


# nArr = nameToNArr(dbSOURCE, name, 10);
# query = ollama.embed(model='llama3.2', input=str(nArr),)
# db = sqlite3.connect(dbVECTOR)
# db.enable_load_extension(True)
# sqlite_vec.load(db)
# db.enable_load_extension(False)

# rows = db.execute(
#   """
#     SELECT
#       rowid,
#       distance
#     FROM vec_items
#     WHERE embedding MATCH ?
#     AND k = 5
#   """,
# [serialize_f32(query.embeddings[0][:256])],
# ).fetchall()
# # print([x[0] for x in rows])

# message = {"message":[]}

# while rows:
#     node = rows.pop()
#     val = rowIdToName(dbSOURCE, str(node[0]), 10)
#     if val != [0]:
#         message["message"]+=[val]



#99129

def pairwise_correlation(A, B):
    am = A - np.mean(A, axis=0, keepdims=True)
    bm = B - np.mean(B, axis=0, keepdims=True)
    return am.T @ bm /  (np.sqrt(
        np.sum(am**2, axis=0,
               keepdims=True)).T * np.sqrt(
        np.sum(bm**2, axis=0, keepdims=True)))


def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)


def deserialize_f32(vector,size=256):
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.unpack(f"{size}f", vector)



def call(PATH,TIMEOUT):
    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor



def _readEmbeddingByKeyId(timeout, key_id=0):
    try:
        db = sqlite3.connect(dbVECTOR)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        x = db.execute("SELECT embedding FROM vec_items WHERE key_id = ? LIMIT 1", [str(key_id),]).fetchall()
        print(key_id, end=": ")
        # print(x)
        return x.pop()
        # while x:
        #     node = x.pop()
        #     print(node)
        return -1

    except Exception as e:
        print("failure")
        print(e)
        
    finally:
        db.close()






def bruteforceKNN(id, eValue):
    print("@@@", end=" ")
    db = sqlite3.connect(dbVECTOR)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)



    query_Row = keyIdToRow(dbSOURCE,id, 10)
    q_image = [float(a) for a in query_Row[5]]
    q_epigenomic = np.frombuffer(query_Row[17],dtype=float, count=16)
    print()
    print()


    rows = db.execute(
      """
        SELECT
          key_id,
          distance
        FROM vec_items
        WHERE embedding MATCH ?
        AND k = 5
      """,
    eValue,
    ).fetchall()
    print([x[0] for x in rows])

    while rows:
        node = rows.pop()
        # print(node[0])
        # print('he')
        # ~> Compare the Features of the query. use
        val = keyIdToRow(dbSOURCE, node[0], 10)

        if val == -2:
        	pass
            # pairwise_correlation(i_vec, a_vec)
            #maximum penalty.
        else:
        	a_image = [float(a) for a in val[5]]  ##store image size exact before writing to file.
        	a_epigenomic = np.frombuffer(val[17],dtype=float, count=16)
        	print("epigenomic", pairwise_correlation(q_epigenomic, a_epigenomic))
        	print("images", pairwise_correlation(q_image, a_image))

 

        		# print(deserialize_f32(a))
            # print([a for a in val])

        # pairwise_correlation(i_vec, a_vec)

    # quit(0)



    # return jsonify(message)

def keyIdToRow(dbPATH=dbSOURCE, key_id=1, timeout=10):
    if key_id==-1:
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        cursor_s.row_factory = sqlite3.Row
        print(key_id)
        cursor_s.execute("SELECT * FROM imag WHERE key_id = (?)", (key_id,))
        row = cursor_s.fetchone()
        cursor_s.close()
        connection_s.close()
        # print(row)
        return row

    except Exception as e:
        cursor_s.close()
        connection_s.close()
        print(e)
        return -2















def nameToKeyID(dbPATH=dbSOURCE, name="", timeout=10):
# def nameToRowId(dbPATH=dbSOURCE, name="", timeout=10):
    print(name)
    if name=="":
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        print(name)
        cursor_s.execute("SELECT key_id FROM imag WHERE name = ?", (name,))
        # cursor_s.execute("SELECT * FROM imag WHERE rowid = ? LIMIT 1", rowID) 
        row = cursor_s.fetchone()
        cursor_s.close()
        connection_s.close()
        # print(row[4])
        # return row
        return row[0]

    except Exception as e:
        cursor_s.close()
        connection_s.close()
        print(e)
        return [0]

def mainProg():
    for i in range(1,99130):
        embedded = _readEmbeddingByKeyId(10, i)
        # print(embedded)

        if embedded!=-1:
            bruteforceKNN(i, embedded)

        print("\n\n")


if __name__ == "__main__":
    mainProg()