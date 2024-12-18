import sqlite3
from typing import Final ,TypedDict

from pathlib import Path
from sqlite_dateconverter import sqlite_date_converter

class DbClass:
    """
        DBの初期化とCURDを担うクラス
        現状はUSER_MASTER_DB_NAMEとSHIFT_SCHEDULE_DB_NAMEの2つのテーブルがある。
        USER_MASTER_DB_NAMEは社員の名前と社員番号を管理する。
        SHIFT_SCHEDULE_DB_NAMEは社員の勤務時間を管理する。
        クラスが初期化されるとDBが作成される。
    """
    def __init__(self,db_path:Path|str="test.db"):
        #日付型を使えるようにする
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
        
## ここからUserDataテーブルのCURD
    def select_userdate_from_name_list(self,search_name:str)-> tuple[tuple[int,int,str], ...] | None:
        """
        名前からNameDataを調べて該当する名前があるかをDBIDと社員番号と名前のTupleで返す。
        2つ以上あったら全部返す。
        Listとは書いてあるけどTupleを返すので注意。
        名前を返すときはスペースを削除する
        """
        result = tuple(
            self.cur.execute(f"""SELECT id,num,name
                            FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} 
                            WHERE name LIKE ?; 
                        """,(f"{search_name[:2]}%",))
        )   
        # idと名前のタプルを返す
        result_tuple:tuple[tuple[int, int,str], ...] = tuple([(t[0], t[1],t[2].replace(" ", "")) for t in result if search_name.replace(" ", "") in t[2].replace(" ", "")])
        return_list:list[tuple[int, int,str],] = []
        #タプルリストに入っている名前と空白を消したserch_nameが一致しているかチェックする
        for t in result_tuple:
            if search_name.replace(" ", "") == t[2]:
                return_list.append(t)
            
        if len(return_list) >= 1:
            return tuple(return_list)
        else: 
            return None
        
    def select_userdate_from_num_list(self,search_num:int)-> tuple[tuple[int,int,str], ...] | None:
        """
            社員番号からNameDataを調べて該当する番号があるかをDBIDと社員番号と名前のTupleで返す。
            2つ以上あったら全部返す。
            Listとは書いてあるけどTupleを返すので注意。
            名前を返すときはスペースを削除する
        """
        result:tuple[tuple[int,int,str]] = tuple(self.con.execute(
                        f"""
                            SELECT id,num,name
                            FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} 
                            WHERE num LIKE ?; 
                        """,(search_num,)))
        result_tuple:tuple[tuple[int, int,str], ...] = tuple([(t[0], t[1],t[2].replace(" ","")) for t in result])
        if len(result_tuple) >= 1:
            return result_tuple
        else:
            return None

    def is_exist_userdate_id(self,search_id:int)-> bool:
        """
            IDが存在するかを調べる
            存在すればTrueを返す
        """
        if self.cur.execute(f"""
            SELECT id
            FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} 
            WHERE id = ?; 
        """,(search_id,)).fetchone():
            return True
        else:
            return False

    def insert_user(self, user_num: int, name: str) -> bool:
        """
        名前と社員番号を登録します。
        成功したらTrueを、番号か名前が被ったらFalseを返します
        """
        # Noneで帰ってこない場合は同姓同名の人が帰ってきているはず。
        if self.select_userdate_from_name_list(name):
            #IDじゃなくて社員番号を（num)を検索する
            if self.select_userdate_from_num_list(user_num):
            # 両方一緒ならば登録しないでFalseを返す
                return False

        self.cur.execute(f"""
            INSERT INTO {self.__dbname_list_dict["USER_MASTER_DB_NAME"]} (num, name)
            VALUES (?, ?);
        """, (user_num, name))
        self.con.commit()
        return True

    # 削除と更新はDBのIDを指定して行う
    def delete_user(self,search_user_id:int)->bool:
        """
            DBIDを指定して削除します。
            成功したらTrueを返します
        """
        #一応UserDataのIDが存在するかを確認
        if not self.is_exist_userdate_id(search_user_id):
            return False
        self.cur.execute(f"""
            DELETE FROM {self.__dbname_list_dict["USER_MASTER_DB_NAME"]}
            WHERE id = ?;
            """,(search_user_id,))
        self.con.commit()
        return True

    def update_user(self,search_user_id:int,new_num:int,new_name:str)->bool:
        """ 
            DBIDを指定して更新します。
            成功したらTrueを返します
            """
        # UserDataのIDが存在するかを確認
        if not self.is_exist_userdate_id(search_user_id):
            return False
        
        # 更新するフィールドを動的に決定
        update_fields: list[str] = []
        update_values: list[int | str] = []
        
        if new_num is not None:
            update_fields.append("num = ?")
            update_values.append(new_num)
        
        if new_name is not None:
            update_fields.append("name = ?")
            update_values.append(new_name)
        
        if not update_fields:
            return False
        
        update_values.append(search_user_id)
        
        self.cur.execute(f"""
            UPDATE {self.__dbname_list_dict["USER_MASTER_DB_NAME"]}
            SET {', '.join(update_fields)}
            WHERE id = ?;
            """, update_values)
        self.con.commit()
        return True


    @property
    def DBNAME_lIST(self):
        return self.__dbname_list_dict


    # def __del__(self):
    #     self.con.close()
    #     self.cur.close()