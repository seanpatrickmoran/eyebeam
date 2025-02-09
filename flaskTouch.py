
import sqlite3
import sqlite_vec
# from ollama import embed
import ollama



dbSOURCE = "/Users/seanmoran/Documents/Master/2024/Dec2024/databaseDUMP/databse6_binary.db";
dbVECTOR = "/Users/seanmoran/Documents/Master/2025/Feb2025/vectorPilot/EB_databaseVEC.db"



def call(PATH,TIMEOUT):
    #only for SOURCE db
    connection = sqlite3.connect(PATH, timeout=TIMEOUT)  # Set timeout to 10 seconds
    cursor = connection.cursor()
    return connection,cursor

def getRowId(dbPATH=dbSOURCE, rowID="", timeout=10):

    if rowID=="":
        return
    #Full DB, not VEC
    connection_s,cursor_s=call(dbPATH,timeout)

    try:
        cursor_s.execute("SELECT * FROM imag WHERE row_id = ? LIMIT 1", rowID) 
        row = cursor_s.fetchone()
        print(row)
        # return row

    except Exception as e:
        print(e)

    finally:
        cursor_s.close()
        connection_s.close()
    



    # def _readDB(offset, limit):
    #     connection_s,cursor_s=call(dbPATH1,timeout)
    #     # connection_t,cursor_t=call(dbPATH2,timeout)
    #     # dbvec = sqlite3.connect(dbPATH2)

    #     try:
    #         db = sqlite3.connect(dbPATH2)
    #         db.enable_load_extension(True)
    #         sqlite_vec.load(db)
    #         db.enable_load_extension(False)
    #         cursor_s.row_factory = sqlite3.Row
    #         # params = (name,)
    #         cursor_s.execute("SELECT rowid, * FROM imag LIMIT ? OFFSET ?", (limit,offset))
    #         row_ids = []
    #         reply = []
    #         for en in cursor_s.fetchall():
    #             row_ids += [en[0]]
    #             reply += [str(en[5])]

    #         # print(reply)
    #         response = ollama.embed(model='llama3.2', input=reply, options={'num_gpus': 99})
    #         # response = ollama.embed(model='llama3.2', input=reply)
    #         # print(response.embeddings)

    #         for idx,embd in enumerate(response.embeddings):
    #             # print(embd[0:256])
    #             db.execute("INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)", [row_ids[idx], serialize_f32(embd[0:256])],)
    #             # print([x for x in db.execute("SELECT * from vec_items").fetchall()])
    #             # print("@@@@@@@@@@")

    #         # print(f"success")

    #     except Exception as e:
    #         print(e)

    #     finally:
    #         cursor_s.close()
    #         connection_s.close()
    #         db.commit()
    #         db.close()





















# def retrieval(SOURCE=dbSOURCE, VECTOR=dbVECTOR):
#     "SELECT * FROM game WHERE id = 1 LIMIT 1;"


    # 1, @dbSOURCE call name, get rowid
    # 2, @dbVECTOR use rowid, fetch embedding
    # 3, @dbVECTOR query dbVECTOR