#testfire

import sqlite3
import sqlite_vec
# from ollama import embed
import ollama
from typing import List
import struct
import datetime


def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)




def call(PATH,TIMEOUT):

    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor


def untouch(dbPATH,timeout):
    db = sqlite3.connect(dbPATH)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    try:
        db.execute("DROP TABLE vec_items")#, (kwargs['tablename'],))
#         print(cursor.fetchall())
        print(f"success")
    except Exception as e:
        print("connection failure")
        print(e)
    finally:
        db.commit()
        db.close()


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
            cursor_s.execute("SELECT rowid, * FROM imag LIMIT ? OFFSET ?", (limit,offset))
            row_ids = []
            reply = []
            for en in cursor_s.fetchall():
                row_ids += [en[0]]
                reply += [str(en[5])]

            print(reply[0])

            # print(reply)
            #response = ollama.embed(model='llama3.2', input=reply, options={'num_gpus': 99})
            # response = ollama.embed(model='llama3.2', input=reply)
            # print(response.embeddings)

            #for idx,embd in enumerate(response.embeddings):
                # print(embd[0:256])
                #db.execute("INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)", [row_ids[idx], serialize_f32(embd[0:256])],)
                # print([x for x in db.execute("SELECT * from vec_items").fetchall()])
                # print("@@@@@@@@@@")
            #    print(index)
            # print(f"success")

        except Exception as e:
            print(e)

        finally:
            cursor_s.close()
            connection_s.close()
            db.commit()
            db.close()

    if not all(i in kwargs for i in ["limit","offset"]):
        raise Exception("need  \"limit\",\"offset\" in kwargs")
    return _readDB(kwargs['offset'],kwargs["limit"])


def mainProg():
    dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
    dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC_byteArr.db"

#    try:
#        _createTable(dbVECTOR, 100)
#    except sqlite3.OperationalError:
#        untouch(dbVECTOR,100)
#        _createTable(dbVECTOR, 100)

    hardLimiter = 5000;

    insert_kwargs = {
        "limit": 50,
#        "offset": 1650,
        "offset": 1900,
        }

    while insert_kwargs["offset"] < hardLimiter:
        tnow = datetime.datetime.now()
        _readSOURCE_writeVECTOR(dbSOURCE, dbVECTOR, 100, **insert_kwargs)
        insert_kwargs["offset"] = insert_kwargs.get("offset", 0) + insert_kwargs.get("limit", 10)
        print(datetime.datetime.now() - tnow)
        print(insert_kwargs)
        # print("written")


if __name__ == "__main__":
    now = datetime.datetime.now()
    mainProg();
    print(datetime.datetime.now() - now)
#     timeit.timeit(setup='''import sqlite3
# import sqlite_vec
# # from ollama import embed
# import ollama
# from typing import List
# import struct
# import timeit''', stmt=mainProg, number=1);




