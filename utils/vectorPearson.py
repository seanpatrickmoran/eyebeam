import sqlite_vec
# from termcolor import colored, cprint

from typing import List
import struct
import datetime
import sqlite3
import json

import numpy as np
import sys

# from scipy.stats import pearsonr

dbSOURCE = "/Users/seanmoran/Documents/Master/2025/Feb2025/database_TEST/database_17_bin.db"
# dbSOURCE = "/Users/seanmoran/Documents/Master/2025/Feb2025/database_TEST/database_14_bin.db"
dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/database_TEST/EB_databaseVEC_14.db"

#99129

colorMap = {
            5: '\x1b[95m',
            4: '\x1b[96m',
            3: '\x1b[92m',
            2:  '\x1b[39m',
            1:  '\x1b[93m',
            0:  '\x1b[91m\x1b[5m'
            # 5: '\x1b[95m\x1b[40m',
            # 4: '\x1b[96m\x1b[40m',
            # 3: '\x1b[92m\x1b[40m',
            # 2:  '\x1b[97m\x1b[40m',
            # 1:  '\x1b[93m\x1b[40m',
            # 0:  '\x1b[91m\x1b[40m\x1b[5m'
            }


store_answer = {"imageScore":np.zeros(99129),
                "epiScore":np.zeros(99129),
                # "histogramScore":np.zeros(99129),
                "p@k":np.zeros(99129),
                }


def pairwise_correlation(A, B):
    am = A - np.mean(A, axis=0, keepdims=True)
    bm = B - np.mean(B, axis=0, keepdims=True)
    return am.T @ bm /  (np.sqrt(
        np.sum(am**2, axis=0,
               keepdims=True)).T * np.sqrt(
        np.sum(bm**2, axis=0, keepdims=True)))


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def serialize_f32(vector: List[float]) -> bytes:
    return struct.pack("%sf" % len(vector), *vector)


def deserialize_f32(vector,size=256):
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
        db.close()
        return x.pop()

    except Exception as e:
        db.close()
        print("failure")
        print(e)
        return -1
        
        



def bruteforceKNN(id, eValue):
    print("@@@", end=" ")
    # print("@@@", end=" ", file=sys.stderr, flush=True)
    db = sqlite3.connect(dbVECTOR)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    query_Row = keyIdToRow(dbSOURCE,id, 10)
    q_vmax  = query_Row[6]
    q_image = [round(float(a)/q_vmax*255) for a in query_Row[5]]
    q_epigenomic = np.frombuffer(query_Row[17],dtype=float, count=16)
    print(len([int(x) for x in query_Row[8]]))
    q_histogram = np.frombuffer(query_Row[8],dtype=int)

    rows = db.execute(
      """
        SELECT
          key_id,
          distance
        FROM vec_items
        WHERE embedding MATCH ?
        AND k = 8
      """,
    eValue,
    ).fetchall()
    print([x[0] for x in rows])
    # print([x[0] for x in rows], file=sys.stderr, flush=True)
    store_answer["p@k"][id] = sum(1-x[1] for x in rows)/len(rows)


    store_epiP = []
    store_imgP = []
    store_histP = []

    while rows:
        node = rows.pop()
        # print(node[0])
        # print('he')
        # ~> Compare the Features of the query. use
        val = keyIdToRow(dbSOURCE, node[0], 10)

        if val == -2 or val[0]==id:
            pass
            # pairwise_correlation(i_vec, a_vec)
            #maximum penalty.
        else:
            a_vmax  = val[6]
            a_image = [round(float(a)/a_vmax*255) for a in val[5]]  ##store image size exact before writing to file.
            a_epigenomic = np.frombuffer(val[17],dtype=float, count=16)
            # a_histogram = np.frombuffer(val[8],dtype=int)
            try:
                epiP = pairwise_correlation(q_epigenomic, a_epigenomic)
            except ValueError as e:
                print(f"ValueError: {e}")
                epi = 0
            try:
                imgP = pairwise_correlation(q_image, a_image)
            except ValueError as e:
                print(f"ValueError: {e}")
                imgP = 0
            # try:
            #     histP = pairwise_correlation(q_histogram, a_histogram)
            # except ValueError as e:
            #     print(f"ValueError: {e}")
            #     histP = 0

            store_epiP += [epiP]
            store_imgP += [imgP]
            # store_histP += [histP]
            # print("epigenomic",epiP)
            # print("images", imgP)

    store_answer["epiScore"][id] = sum(store_epiP)/len(store_epiP)
    store_answer["imageScore"][id] = sum(store_imgP)/len(store_imgP)
    # store_answer["histogramScore"][id] = sum(store_histP)/len(store_histP)

    # store_answer["p@k"][id] = sum(x[1] for x in rows)/len(rows)
    logging=""
    for pname in ["epiScore", "imageScore", "p@k"]:
        logging +=  pname+": "
    # for pname in ["epiScore", "imageScore", "histogramScore", "p@k"]:
        # print(,end="")
        _store = round(store_answer[pname][id] * 100 // 20 + 1)
        _store = _store if _store > 0 else 0

        # print(f"{colorMap[_store]}{store_answer[pname][id]}\x1b[0m",end=" ")
        logging += f"{colorMap[_store]}{store_answer[pname][id]}\x1b[0m" + " "
    logging += "\n"

    print(logging)
    # print(logging, file=sys.stderr, flush=True)
    # print("epiScore: ",  store_answer["epiScore"][id], ", imageScore: ", store_answer["imageScore"][id] , ", p@k: ", store_answer["p@k"][id])


def keyIdToRow(dbPATH=dbSOURCE, key_id=1, timeout=10):
    if key_id==-1:
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        cursor_s.row_factory = sqlite3.Row
        # print(key_id)
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
    print(name)
    if name=="":
        return

    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        print(name)
        cursor_s.execute("SELECT key_id FROM imag WHERE name = ?", (name,))
        row = cursor_s.fetchone()
        cursor_s.close()
        connection_s.close()
        return row[0]

    except Exception as e:
        cursor_s.close()
        connection_s.close()
        print(e)
        return -2

def mainProg():
    for i in range(0,99130):
        embedded = _readEmbeddingByKeyId(10, i)
        # print(embedded)

        if embedded!=-1:
            bruteforceKNN(i, embedded)

        with open("021925_vector_pearson_analytics.json", "w") as zug:
            zug.write(json.dumps(store_answer,cls=NumpyEncoder))


if __name__ == "__main__":
    mainProg()