import faiss
import sqlite3
from sys import getsizeof
from typing import List
import struct
import numpy as np


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

def runMain():
    index = faiss.read_index("/Users/seanmoran/Projects/pyBeam/eyeBeam/faiss.test.index")
    print("boot index")


    rows = getEverything(dbSQLITE3VEC);
    # print(rows)
    print('rad')

    ### faiss here.
    d = 256                           # dimension
    nb = len(rows)                      # database size
    nq = nb//10                       # nb of queries
    xb=np.array([np.array(xi[1]) for xi in rows]).astype('float32')
    # xb = np.random.random((nb, d)).astype('float32')
    xb[:, 0] += np.arange(nb) / 1000.
    xq = np.random.random((nq, d)).astype('float32')
    xq[:, 0] += np.arange(nq) / 1000.

    print(getsizeof(xb))
    print(xb.nbytes)

    k=50
    print("added index")
    D, I = index.search(xb[:5], k) # sanity check
    print(I)
    print(D)
    index.nprobe = 10              # make comparable with experiment above
    D, I = index.search(xq, k)     # search
    print(I[-5:])



if __name__ == "__main__":
    runMain()
