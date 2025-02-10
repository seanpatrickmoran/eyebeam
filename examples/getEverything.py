# import faiss
import sqlite3
import sqlite_vec
from typing import List
import struct

import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)




dbSQLITE3VEC = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/SQLITE_databaseVEC.db"

dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"

def call(PATH,TIMEOUT):

    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor




def getEverything(dbPATH=dbVECTOR, timeout=10):


    #Full DB, not VEC
    # connection_s,cursor_s=call(dbPATH,timeout)

    try:
        db = sqlite3.connect(dbPATH)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        row = db.execute("SELECT * from vector_table").fetchall()
        # cursor_s.execute("SELECT embedding FROM vec_items")

        # row = cursor_s.fetchall()
        # print(row)
        # cursor_s.close()
        # connection_s.close()
        db.close()
        return row

    except Exception as e:
        # cursor_s.close()
        # connection_s.close()
        db.close()
        print(e)
        return [0]






def runMain():
    Row = getEverything(dbSQLITE3VEC);
    print(Row)







if __name__ == "__main__":
    runMain()
