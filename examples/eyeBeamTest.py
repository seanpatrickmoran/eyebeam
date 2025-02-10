#testfire

import sqlite3
import sqlite_vec
# from ollama import embed
import ollama
from typing import List
import struct


def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)




def call(PATH,TIMEOUT):

    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor

def _createTable(dbPATH, timeout,**kwargs):

    # connection,cursor=call(dbPATH,timeout)
    try:
        db = sqlite3.connect(dbPATH)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        # cursor = connection.execute("CREATE TABLE vec_items USING vec0(embedding float[256])")
        db.execute("CREATE VIRTUAL TABLE vec_items USING vec0(embedding float[256])")
        # cursor = connection.execute("CREATE TABLE imag(name, dataset, condition, coordinates, numpyarr, viewing_vmax, dimensions, hic_path, PUB_ID, resolution, norm, meta)")
        print("table make; success")
        # db.close()
    finally:
        db.close()
        # cursor.close()
        # connection.close()


    # sqlite_vec.load(db)
def _readSOURCE_writeVECTOR(dbPATH1, dbPATH2,timeout,**kwargs):
# def _readMatchAllTable(dbPATH,timeout,**kwargs):
    def _readDB(offset, limit):
        connection_s,cursor_s=call(dbPATH1,timeout)
        # connection_t,cursor_t=call(dbPATH2,timeout)
        # dbvec = sqlite3.connect(dbPATH2)

        try:
            db = sqlite3.connect(dbPATH2)
            db.enable_load_extension(True)
            sqlite_vec.load(db)
            db.enable_load_extension(False)
            cursor_s.row_factory = sqlite3.Row
            # params = (name,)
            cursor_s.execute("SELECT * FROM imag LIMIT ? OFFSET ?", (limit,offset))
            reply = []
            # data = tuple(x for x in data)
            for en in cursor_s.fetchall():
                print()
                # print(*en)
                reply += [str(en[0])]

            print(reply)
            # embeddings = tuple(ollama.embed(model='llama3.2', input=x) for x in reply)
            response = ollama.embed(model='llama3.2', input=reply)
            print(response.embeddings)
            # cursor.executemany("INSERT INTO  vec_items(rowid, embedding) VALUES (?, ?)", [item[0], serialize_f32(item[1])],)
            for idx,embd in enumerate(response.embeddings):
                # print(embd)
                print(embd[0:256])
                # print(serialize_f32(embd[0:256]))
                db.execute("INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)", [idx+offset, serialize_f32(embd[0:256])],)
                print([x for x in db.execute("SELECT * from vec_items").fetchall()])
                print("@@@@@@@@@@")
            print(f"success")

        except Exception as e:
            print(e)

        finally:
            cursor_s.close()
            connection_s.close()
            db.commit()
            db.close()
            # cursor_t.close()
            # connection_t.close()

        # return reply

    if not all(i in kwargs for i in ["limit","offset"]):
        raise Exception("need  \"limit\",\"offset\" in kwargs")
    return _readDB(kwargs['offset'],kwargs["limit"])


def mainProg():
    dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
    dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/databaseVEC.db"

    insert_kwargs = {
        "limit": 5,
        "offset"  : 0,
        }

    _createTable(dbVECTOR, 100)
    _readSOURCE_writeVECTOR(dbSOURCE, dbVECTOR, 100, **insert_kwargs)
    print("written")




if __name__ == "__main__":
    mainProg();
