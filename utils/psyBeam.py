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
        db.execute("CREATE VIRTUAL TABLE vec_items USING vec0(key_id integer primary key, embedding float[256])")
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

        try:
            db = sqlite3.connect(dbPATH2)
            db.enable_load_extension(True)
            sqlite_vec.load(db)
            db.enable_load_extension(False)
            cursor_s.row_factory = sqlite3.Row
            cursor_s.execute("SELECT * FROM imag LIMIT ? OFFSET ?", (limit,offset))
            print("..")
            row_ids = []
            reply = []
            for en in cursor_s.fetchall():
                if len(en[5])!=16900:
                    continue
                row_ids += [en[0]]
                reply += [en[5]]



                """
                table schema:

                imag(
                    0:  key_id
                    1:  name, 
                    2:  dataset, 
                    3:  condition, 
                    4:  coordinates, 
                    5:  numpyarr, 
                    6:  viewing_vmax, 
                    7:  dimensions, 
                    8:  hic_path, 
                    9:  PUB_ID, 
                    10: resolution, 
                    11: norm, 
                    12: meta
                    )
                """
                row_ids += [en[0]]
                reply += [en[5]]

                """
                plan is change table...

                imag(
                    0:  key_id
                    1:  name, 
                    2:  dataset, 
                    3:  condition, 
                    4:  coordinates, 
                    5:  numpyarr, 
                    6*  greyscale256bitcolorHistogram (blob),
                    6:  viewing_vmax, 
                    7:  dimensions, 
                    8:  hic_path, 
                    9:  PUB_ID, 
                    10: resolution, 
                    11: norm, 
                    12: meta
                    )


                and then concat. first 6*, then 5, then 10.
                reply += [str(en[6].extend(en[5]).extend(en[10])]

                """

            # response = ollama.embed(model='llama3.2', input=reply, options={'num_gpus': 99})

            print(type(reply[0]))

            for idx,embd in enumerate(reply):
                # print(embd)
                # print(embd[0:256])
                # unpacked_float_single = struct.unpack('>f', packed_float_single)[0]
                db.execute("INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)", [row_ids[idx], embd[:1024]],)
                # print([x for x in db.execute("SELECT * from vec_items").fetchall()])
                # print("@@@@@@@@@@")

            print(f"success")


        except sqlite3.OperationalError as e:
            # the limiter overflows whatever is left.
            # just read everything left.

            # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            # print([len(x) for x in reply])
            for x in range(len(reply)):
                if len(reply[x])!=16900:
                    print(row_ids[x])
                    continue
                db.execute("INSERT INTO vec_items(key_id, embedding) VALUES (?, ?)", [row_ids[x], reply[x][:1024]],)

            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            print(e)


        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
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
    dbSOURCE = "/Users/sean/Documents/Master/2025/Feb2025/sourceTables/database_9_bin.db"
    # dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
    # dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"
    dbVECTOR = "/Users/sean/Documents/Master/2025/Feb2025/embeddedLoops/false_databaseVEC_9.db"

    try:
        _createTable(dbVECTOR, 100)
    except sqlite3.OperationalError:
        untouch(dbVECTOR,100)
        _createTable(dbVECTOR, 100)

    hardLimiter = 600000;
    #check length of table

    insert_kwargs = {
        "limit": 2048,
#        "offset": 1650,
        "offset": 0,
        }

    while insert_kwargs["offset"] < hardLimiter:
        tnow = datetime.datetime.now()
        _readSOURCE_writeVECTOR(dbSOURCE, dbVECTOR, 100, **insert_kwargs)
        insert_kwargs["offset"] = insert_kwargs.get("offset", 0) + insert_kwargs.get("limit", 10)
        print(datetime.datetime.now() - tnow, datetime.datetime.now())
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




