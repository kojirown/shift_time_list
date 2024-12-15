from pprint import pprint
from typing import Final
from datetime import datetime
from makelist import make_fake_data
from DbClass import DbClass
from insert_date import make_current_month_shift , insert_shift_data

default_db_path = r".\test.db"

def main_sqlite(db_path:str,insert_user_num:int|None=False) -> DbClass:
    db = DbClass(db_path)

    if db.DBNAME("USER_MASTER_DB_NAME") not in (ex[0] for ex in db.cur.execute("SELECT name FROM sqlite_master").fetchall()):
        db.cur.execute(f"CREATE TABLE {db.DBNAME("USER_MASTER_DB_NAME")}(id integer primary key autoincrement,num integra,name text,address text);")
        db.con.commit()

    if db.DBNAME("SHIFT_SCHEDULE_DB_NAME") not in (ex[0] for ex in db.cur.execute("SELECT name FROM sqlite_master").fetchall()):
        db.cur.execute(f"""CREATE TABLE {db.DBNAME("SHIFT_SCHEDULE_DB_NAME")}(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            starttime DATETIME,
                            endtime DATETIME,
                            FOREIGN KEY (user_id) REFERENCES {db.DBNAME("USER_MASTER_DB_NAME")}(id)
                            );
                            """)
        db.con.commit()

    
    if insert_user_num:
        insert_data_list:list[dict] = make_fake_data(insert_user_num)

        db.cur.executemany(f"INSERT INTO {db.DBNAME("USER_MASTER_DB_NAME")}(num,name,address) VALUES (:ID, :Name, :Address);" ,insert_data_list)
        db.con.commit()
    #select_db(db)
    select_userdate_from_name(db,"太田 翼")
    return(db)

def select_db(db:DbClass):
    result = db.cur.execute("SELECT id,num,name,address FROM UserData;")
    pprint(list(result))


def select_userdate_from_name(db:DbClass,search_name:str)-> int|None:
    result:list = list(
        db.cur.execute(f"""SELECT id,name \
                        FROM {db.DBNAME("USER_MASTER_DB_NAME")} \
                        WHERE name LIKE ?; \
                    """,(f"{search_name[:2]}%",))
    )   
    result_tuple:list = [t[0] for t  in result if search_name.replace(" ","") in t[1].replace(" ","")]
    if len(result_tuple) == 1:
        return result_tuple[0]
    else: 
        return None
    
def select_user_id(db:DbClass)-> list[int]:
    result:list[tuple[int]] = list(
        db.cur.execute(f"""
            select id
            from {db.DBNAME("USER_MASTER_DB_NAME")};
            """
        )
    )
    return [l[0] for l in  result]
    
    
def insert_shift(db:DbClass ,user_id:int,input_datemonth:datetime=datetime.today()):
    month_shift_data_list:list = make_current_month_shift(input_datemonth,user_id)
    # for daily_shift in month_shift_data_list:
    #     insert_shift_data(db,daily_shift)
    insert_shift_data(db,month_shift_data_list)


if __name__ == '__main__':
    db = main_sqlite(default_db_path)
    user_id_list = select_user_id(db)
    for month in range(1,12):

        for i in user_id_list:
            print(f"----user_id:{i}---------------")
            insert_shift(db,i,datetime(2024,month,1))
            print("done.")