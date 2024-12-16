from DbClass import DbClass
class test_classinit():
    db = DbClass(":memory:")
    dblist:list[str] = [t[2] for t in  db.cur.execute(f"""
        SELECT * 
        FROM sqlite_master
        WHERE type='table'; 
    """).fetchall()]

    assert set(db.DBNAME_lIST.values()) <= set(dblist) 


    