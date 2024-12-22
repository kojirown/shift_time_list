import pytest
from datetime import datetime ,date
from DbClass import DbClass
from datetime import datetime
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

@pytest.fixture
def make_test_usrdata():
    db = DbClass(":memory:")
    db.cur.executemany(f"""
    INSERT INTO {db.DBNAME_lIST["USER_MASTER_DB_NAME"]}
    (num,name)
    VALUES
    (?,?);
    """,((100,"testname"),(300,"山田 太郎"),(301,"山田太郎")))
    db.con.commit()
    return db

@pytest.fixture
def make_shift_data():
    db = DbClass(":memory:")
    db.cur.executemany(f"""
    INSERT INTO {db.DBNAME_lIST["USER_MASTER_DB_NAME"]}
    (num,name)
    VALUES
    (?,?);
    """,((100,"testname"),(300,"山田 太郎"),(301,"山田太郎")))
    db.con.commit()
    shift_data = [(1,datetime.fromisoformat("2024-01-01T10:00"), datetime.fromisoformat("2024-01-01T18:00")), 
        (1,datetime.fromisoformat("2024-01-02T10:00"), datetime.fromisoformat("2024-01-02T18:00")),
        (2,datetime.fromisoformat("2024-01-02T12:00"), datetime.fromisoformat("2024-01-03T15:00"))]
    for data in shift_data:
        db.insert_shift_data((data[0], data[1],data[2]))
    return db



# DbClassのCRUDに関するテスト
# テスト用のデータを作成するためDbClassのインスタンスを作成してInsartでダミーデータを入れる
# その後、select_userdate_from_name_listでデータが存在するかを確認する
# その後、delete_userでデータを削除し、再度select_userdate_from_name_listでデータが存在しないかを確認する
class Test_DbclassCRUDTests():
    """
        DbClassのCRUDに関するテスト

    """ 


    # selectメゾットのテスト
    def test_select(self,make_test_usrdata: DbClass):
        db = make_test_usrdata
        # select_fromはtuple[tuple]を返すので注意！！
        result = db.select_userdate_from_name_list("testname")
        assert result is not None, "Expected non-None result"
        assert result[0] == (1, 100, "testname"), f"Expected (100, 'testname'), but got {result[0]}"
        
        result = db.select_userdate_from_num_list(100)
        assert result is not None, "Expected non-None result"
        
        result = db.select_userdate_from_name_list("testname2")
        assert result is None, f"Expected None, but got {result}"
        
        result = db.select_userdate_from_num_list(101)
        assert result is None, f"Expected None, but got {result}"

        result = db.select_userdate_from_name_list("山田 太郎")
        assert result is not None, "Expected non-None result"
        assert len(result) == 2, f"Expected 2, but got {len(result)}"
        assert result[0] == (2, 300, "山田太郎"), f"Expected (2, 300, '山田太郎'), but got {result[0]}"
        assert result [1] == (3, 301, "山田太郎"), f"Expected (3, 301, '山田太郎'), but got {result[1]}"

    # insartメゾットのテスト
    def test_insert(self):
        db = DbClass(":memory:")
        assert db.insert_user(100,"testname") , "Expected True"

        result = db.select_userdate_from_name_list("testname")
        assert result is not None, "Expected non-None result"
        assert result[0] == (1,100, "testname"), f"Expected (1,100, 'testname'), but got {result[0]}"
        
        assert db.select_userdate_from_num_list(100)
        assert result is not None, "Expected non-None result"
        assert result[0] == (1,100, "testname"), f"Expected (1,100, 'testname'), but got {result[0]}"

    def test_delete(self,make_test_usrdata: DbClass):
        """
        test_deleteメソッドは、データベースからユーザーを削除する機能をテストします。
        テスト内容:
        1. "testname"という名前のユーザーをデータベースから取得し、そのIDを使用して削除を実行します。
        2. ユーザーが正しく削除されたことを確認します。
        3. メモリ上のデータベースに新しいユーザーを挿入し、更新操作をテストします。
        4. 更新後のユーザー情報が正しく取得できることを確認します。
        5. 古いユーザー情報が存在しないことを確認します。
        """
        db= make_test_usrdata
        assert (db_result := db.select_userdate_from_name_list("testname")), "No user data found"
        result_db_id = db_result[0][0]
        assert db.delete_user(result_db_id)
        assert not db.select_userdate_from_name_list("testname")
        assert not db.select_userdate_from_num_list(100)
    
    
        db = DbClass(":memory:")
        assert db.insert_user(100,"testname")
        assert db.update_user(1,101,"testname2")
        assert (db_result := db.select_userdate_from_name_list("testname2")), "No user data found"
        assert db_result[0] == (1,101,"testname2")
        assert db_result[0] == (1,101,"testname2")
        assert not db.select_userdate_from_name_list("testname")
        assert not db.select_userdate_from_num_list(100)

    def test_insert_shift_Data(self, make_test_usrdata: DbClass):
        """
        test_insert_shift_Dataメソッドは、シフトデータをデータベースに挿入する機能をテストします。
        テスト内容:
        1. ユーザーIDを使用してシフトデータを挿入します。
        2. シフトデータが正しく挿入されたことを確認します。
        3. ユーザーIDを使用してシフトデータを取得し、正しいデータが取得できることを確認します。
        """
        db = make_test_usrdata
        result = db.select_userdate_from_name_list("testname")
        assert result is not None, "No user data found"
        user_id = result[0][0]
        shift_data = [(user_id,datetime.fromisoformat("2024-01-01T10:00"), datetime.fromisoformat("2024-01-01T18:00")), 
            (user_id,datetime.fromisoformat("2024-01-02T10:00"), datetime.fromisoformat("2024-01-02T18:00"))]
        for i,data in enumerate(shift_data):
            assert db.insert_shift_data((data[0], data[1],data[2])), f"Failed to insert shift data {i+1}"
        select_result = db.select_by_user_shift_data(user_id)
        assert select_result is not None, "No shift data found"
        assert len(select_result) == 2, "Expected 2 shift data"
        for i, t in  enumerate(select_result):
            assert t["user_id"] == user_id, f"Expected user_id to match in Element:{i}"
            assert t["starttime"] == shift_data[i][1], f"Expected starttime to match in Element:{i}"
            assert t["endtime"] == shift_data[i][2], f"Expected endtime to match in Element:{i}"
    
    def test_select_shift_Data(self, make_test_usrdata: DbClass):
        """
        test_select_shift_Dataメソッドは、シフトデータを取得する機能をテストします。
        テスト内容:
        1. ユーザーIDを使用してシフトデータを取得します。
        2. 正しいデータが取得できることを確認します。
        """
        db = make_test_usrdata
        result = db.select_userdate_from_name_list("testname")
        assert result is not None, "No user data found"
        user_id = result[0][0]
        shift_data = [(user_id,datetime.fromisoformat("2024-01-01T10:00"), datetime.fromisoformat("2024-01-01T18:00")), 
            (user_id,datetime.fromisoformat("2024-01-02T10:00"), datetime.fromisoformat("2024-01-02T18:00")),
            (2,datetime.fromisoformat("2024-01-02T12:00"), datetime.fromisoformat("2024-01-03T15:00"))]
        for i,data in enumerate(shift_data):
            db.insert_shift_data((data[0], data[1],data[2]))
        select_result = db.select_by_user_shift_data(user_id)
        assert select_result is not None, "No shift data found"
        assert len(select_result) == 2, "Expected 2 shift data"
        for i, t in  enumerate(select_result):            
            assert t["user_id"] == user_id, f"Expected user_id to match in Element:{i}"
            assert t["starttime"] == shift_data[i][1], f"Expected starttime to match in Element:{i}"
            assert t["endtime"] == shift_data[i][2], f"Expected endtime to match in Element:{i}"

    def test_select_shift_by_id(self, make_test_usrdata: DbClass):
        db = make_test_usrdata
        user_id = 1
        shift_data = [(user_id,datetime.fromisoformat("2024-01-01T10:00"), datetime.fromisoformat("2024-01-01T18:00")), 
            (user_id,datetime.fromisoformat("2024-01-02T10:00"), datetime.fromisoformat("2024-01-02T18:00")),
            (2,datetime.fromisoformat("2024-01-02T12:00"), datetime.fromisoformat("2024-01-03T15:00"))]
        for data in shift_data:
            print(db.insert_shift_data((data[0], data[1],data[2])))
        select_result = db.select_by_shift_id(1)
        assert select_result is not None, "No shift data found"
        assert select_result["user_id"] == user_id, f"Expected user_id to match in Element"
        assert select_result["starttime"] == shift_data[0][1], f"Expected starttime to match in Element"
        assert select_result["endtime"] == shift_data[0][2], f"Expected endtime to match in Element"

    def test_update_shift_Data(self, make_shift_data: DbClass):
        """
        test_update_shift_Dataメソッドは、シフトデータを更新する機能をテストします。
        テスト内容:
        1. updte_dataのパラメータでシフトデータを更新します。
        2. 更新後のデータがuser_dateと正しいことを確認します。

        """
        db = make_shift_data
        target_shift_id = 1
        update_data:tuple[int,datetime,datetime] = (target_shift_id,datetime.fromisoformat("2024-01-01T10:00"), datetime.fromisoformat("2024-01-01T18:00"))
        assert db.update_shift_data(update_data[0],update_data[1],update_data[2]) is not None, "Failed to update shift data"
        # 更新後のデータを取得
        select_result = db.select_by_shift_id(target_shift_id)
        assert select_result is not None, "No shift data found"
        assert select_result["user_id"] == update_data[0], f"Expected user_id to match"
        assert select_result["starttime"] == update_data[1], f"Expected starttime to match"
        assert select_result["endtime"] == update_data[2], f"Expected endtime to match"

    def test_delete_shift_Data(self, make_shift_data: DbClass):
        """
        test_delete_shift_Dataメソッドは、シフトデータを削除する機能をテストします。
        テスト内容:
        1. 削除するシフトデータのIDを指定して削除を実行します。
        2. 削除後のデータが存在しないことを確認します。
        """
        db = make_shift_data
        target_shift_id = 1
        assert db.delete_shift_data(target_shift_id) is not None, "Failed to delete shift data"
        select_result = db.select_by_shift_id(target_shift_id)
        assert select_result is None, "Shift data still exists"
        assert db.select_by_shift_id(2) , "Shift data not found"
