import pytest
from DbClass import DbClass
class TestDBclassinit():
    """
        DbClassの初期化に関するテスト

    """ 
    db = DbClass(":memory:")
    dblist:list[str] = [t[2] for t in  db.cur.execute(f"""
        SELECT * 
        FROM sqlite_master
        WHERE type='table'; 
    """).fetchall()]

    assert set(db.DBNAME_lIST.values()) <= set(dblist) 


# DbClassのCRUDに関するテスト
# テスト用のデータを作成するためDbClassのインスタンスを作成してInsartでダミーデータを入れる
# その後、select_userdate_from_name_listでデータが存在するかを確認する
# その後、delete_userでデータを削除し、再度select_userdate_from_name_listでデータが存在しないかを確認する
class Test_DbclassCRUDTests():
    """
        DbClassのCRUDに関するテスト

    """ 
    db = DbClass(":memory:")
    # テスト用のデータを作成
    # curを使って自力で初期データをInsertする
    # selectのテストのために日本語名と同姓同名の名前も作成する

    db.cur.executemany(f"""
        INSERT INTO {db.DBNAME_lIST["USER_MASTER_DB_NAME"]}
        (num,name)
        VALUES
        (?,?);
    """,((100,"testname"),(300,"山田 太郎"),(301,"山田太郎")))
    db.con.commit()
    # selectメゾットのテスト
    def test_select(self):
        # select_fromはtuple[tuple]を返すので注意！！
        result = self.db.select_userdate_from_name_list("testname")
        assert result is not None, "Expected non-None result"
        assert result[0] == (1, 100, "testname"), f"Expected (100, 'testname'), but got {result[0]}"
        
        result = self.db.select_userdate_from_num_list(100)
        assert result is not None, "Expected non-None result"
        
        result = self.db.select_userdate_from_name_list("testname2")
        assert result is None, f"Expected None, but got {result}"
        
        result = self.db.select_userdate_from_num_list(101)
        assert result is None, f"Expected None, but got {result}"

        result = self.db.select_userdate_from_name_list("山田 太郎")
        assert len(result) == 2, f"Expected 2, but got {len(result)}"
        assert result[0] == (2, 300, "山田太郎"), f"Expected (2, 300, '山田太郎'), but got {result[0]}"
        assert result [1] == (3, 301, "山田太郎"), f"Expected (3, 301, '山田太郎'), but got {result[1]}"

    # insartメゾットのテスト
    def test_insert(self):
        self.db = DbClass(":memory:")
        assert self.db.insert_user(100,"testname") , "Expected True"

        result = self.db.select_userdate_from_name_list("testname")
        assert result is not None, "Expected non-None result"
        assert result[0] == (1,100, "testname"), f"Expected (1,100, 'testname'), but got {result[0]}"
        
        assert self.db.select_userdate_from_num_list(100)
        assert result is not None, "Expected non-None result"
        assert result[0] == (1,100, "testname"), f"Expected (1,100, 'testname'), but got {result[0]}"

    def test_delete(self):
        result_db_id = self.db.select_userdate_from_name_list("testname")[0][0]
        assert self.db.delete_user(result_db_id)
        assert not self.db.select_userdate_from_name_list("testname")
        assert not self.db.select_userdate_from_num_list(100)
    
    def test_update(self):
        self.db = DbClass(":memory:")
        assert self.db.insert_user(100,"testname")
        assert self.db.update_user(1,101,"testname2")
        assert self.db.select_userdate_from_name_list("testname2")[0] == (1,101,"testname2")
        assert self.db.select_userdate_from_num_list(101)[0] == (1,101,"testname2")
        assert not self.db.select_userdate_from_name_list("testname")
        assert not self.db.select_userdate_from_num_list(100)