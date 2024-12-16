import sqlite3
from typing import Final ,TypedDict
from pathlib import Path
from sqlite_dateconverter import sqlite_date_converter

class DbClass:
    """
        DBの初期化とCURDを担うクラス
    """
    def __init__(self,db_path:Path|str="test.db"):
        sqlite_date_converter.sqlite_date_converter_init()
        self.con = sqlite3.connect(Path(db_path),detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cur = self.con.cursor()
        #外部制約をONに
        self.cur.execute("PRAGMA foreign_keys = true")
        self.con.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DDL,False)
        self.__dbname_list_dict:Final[dict[str,str]] = {
            "USER_MASTER_DB_NAME":"UserData",
            "SHIFT_SCHEDULE_DB_NAME":"ShiftSchedule"
        }
        # テーブルがなければ初期化
        if self.__dbname_list_dict["USER_MASTER_DB_NAME"] not in (ex[0] for ex in self.cur.execute("SELECT name FROM sqlite_master").fetchall()):
            self.cur.execute(f"CREATE TABLE {self.__dbname_list_dict["USER_MASTER_DB_NAME"]}(id integer primary key autoincrement,num integra,name text,address text);")
            self.con.commit()

        if self.__dbname_list_dict["SHIFT_SCHEDULE_DB_NAME"] not in (ex[0] for ex in self.cur.execute("SELECT name FROM sqlite_master").fetchall()):
            self.cur.execute(f"""CREATE TABLE {self.__dbname_list_dict["SHIFT_SCHEDULE_DB_NAME"]}(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                starttime DATETIME,
                                endtime DATETIME,
                                FOREIGN KEY (user_id) REFERENCES {self.__dbname_list_dict["USER_MASTER_DB_NAME"]}(id)
                                );
                                """)
            self.con.commit()
        

    def select_userdate_from_name_list(self,search_name:str)-> tuple[int,str]|None:
        """
            名前からNameDataを調べて該当する名前があるかを番号と名前のTupleで返す。
            2つ以上あったら全部返す。
            Listとは書いてあるけどTupleを返すので注意。
        """
        result:list = list(
            self.cur.execute(f"""SELECT id,name 
                            FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} 
                            WHERE name LIKE ?; 
                        """,(f"{search_name[:2]}%",))
        )   
        result_tuple:tuple[int,str]|tuple = tuple([t[0] for t  in result if search_name.replace(" ","") in t[1].replace(" ","")])
        if len(result_tuple) >= 1:
            return result_tuple
        else: 
            return None
        
    def select_userdate_from_num_list(self,search_num:int)-> tuple[tuple[int,str]]|None:
        """
            番号からNameDataを調べて該当する名前があるかを番号と名前のTupleで返す。
            2つ以上あったら全部返す。
            Listとは書いてあるけどTupleを返すので注意。
        """
        id_search_result:tuple[tuple[int,str]] = tuple(self.con.execute(
                        f"""
                            SELECT id
                            FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} 
                            WHERE id =  LIKE ?; 
                        """,(search_num,)))
        if len(id_search_result) >= 1:
            return id_search_result
        else :
            None
        

    def insaert_user(self,num:int,name:str) -> bool:
        """
        名前と社員番号を登録します。
        成功したらTrueを、番号か名前が被ったらFalseを返します
        """
        if self.select_userdate_from_name_list(name):
            return False
        id_search_result:tuple[tuple[int,str]] = tuple(self.con.execute(
                            f"""
                            SELECT id
                            FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} 
                            WHERE id =  LIKE ?; 
                            """,))
        return False

    @property
    def DBNAME_lIST(self):
        return self.__dbname_list_dict


    # def __del__(self):
    #     self.con.close()
    #     self.cur.close()