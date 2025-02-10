#testfire

import sqlite3
import sqlite_vec
# from ollama import embed
import ollama

def call(PATH,TIMEOUT):

    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor



    # sqlite_vec.load(db)
def _readSOURCE(dbPATH,timeout,**kwargs):
# def _readMatchAllTable(dbPATH,timeout,**kwargs):
    def _readDB(offset, limit):
        # connection_s,cursor_s=call(dbPATH,timeout)
        db = sqlite3.connect(dbPATH)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        try:
            # db.row_factory = sqlite3.Row
            # params = (name,)
            print(([x for x in db.execute("SELECT rowid from vec_items").fetchall()]))
            # print

            # reply = []
            # data = tuple(x for x in data)
            # for en in db.fetchall():
                # print()
                # print(*en)
                # reply += [str(en[4])]

            # embeddings = tuple(ollama.embed(model='llama3.2', input=x) for x in reply)
            # embeddings = ollama.embed(model='llama3.2', input=reply)
            # print(embeddings)
            # cursor.executemany("INSERT INTO  vec_items(rowid, embedding) VALUES (?, ?)", [item[0], serialize_f32(item[1])],)
            # for idx,embd in enumerate(embeddings):
                # cursor_t.execute("INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)", [idx+offset, serialize_f32(embd[5][:256])],)
            # print(f"success")

        except Exception as e:
            print(e)

        finally:
            db.close()
            # connection_s.close()
            # cursor_t.close()
            # connection_t.close()

        # return reply

    if not all(i in kwargs for i in ["limit","offset"]):
        raise Exception("need  \"limit\",\"offset\" in kwargs")
    return _readDB(kwargs['offset'],kwargs["limit"])


def mainProg():
    # dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
    dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"

    insert_kwargs = {
        "limit": 10,
        "offset"  : 0,
        }

    _readSOURCE(dbVECTOR, 100, **insert_kwargs)
    print("done")

    


if __name__ == "__main__":
    mainProg();
