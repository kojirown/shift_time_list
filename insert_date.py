from pprint import pprint
from datetime import datetime,timedelta,time 
import random
from typing import NamedTuple ,Any
from DbClass import DbClass
import sqlite3

# 後でここの大本に型を移植する
class ShiftDataTyple(NamedTuple):
    user_id: int
    start_datatime: datetime
    end_datetime: datetime



def make_current_month_shift(current_month_date:datetime,user_id:int) ->list[ShiftDataTyple]:
    current_month_date_count:datetime = current_month_date.replace(day=1)
    return_list:list[ShiftDataTyple] = list()
    while True:
        # 土日はなし
        if current_month_date_count.weekday() in [5,6]:
            current_month_date_count += timedelta(days=1)
            continue
        start_time:datetime = current_month_date_count.replace(hour=random.randrange(7,12,1)) - timedelta(minutes=random.randrange(15))
        end_time:datetime = make_shift(start_time) 
        return_list.append(ShiftDataTyple(user_id,start_time,end_time))
        current_month_date_count += timedelta(days=1)
        # do~whileの代わり
        if not current_month_date.month == current_month_date_count.month:
            break
    return return_list

        

def make_shift(start_time:datetime)-> datetime:
    RANDOM_TIME = 10
    SHIFT_TIME_LIST:list[int] = [3,5,7]
    end_time = random.choices(SHIFT_TIME_LIST,[20,30,50])[0]


    return start_time + timedelta(hours=end_time,minutes=random.randrange(RANDOM_TIME))

def insert_shift_data(db:DbClass,daily_shift_data:ShiftDataTyple|list[ShiftDataTyple]):
    # check_data:tuple[int,datetime,datetime]|None =  tuple(
    # db.cur.execute(f"""
    #     SELECT id,starttime,endtime
    #     FROM {db.DBNAME("SHIFT_SCHEDULE_DB_NAME")}
    #     WHERE user_id = ? AND starttime = ? AND endtime = ?;
    # """,daily_shift_data)
    # )
    # if check_data:
    #     print(check_data)
    # else:
    if type(daily_shift_data) is list:
        param_list:list[Any] = [tuple(t) for t in daily_shift_data]
        db.cur.executemany(f"""
            INSERT INTO {db.DBNAME("SHIFT_SCHEDULE_DB_NAME")} (user_id,starttime,endtime)
            VALUES(?,?,?);
        """,param_list)
    else :
        db.cur.execute(f"""
            INSERT INTO {db.DBNAME("SHIFT_SCHEDULE_DB_NAME")} (user_id,starttime,endtime)
            VALUES(?,?,?);
        """,tuple(daily_shift_data))
    db.con.commit()



if __name__ == '__main__':
    current_date = datetime(2024,10,15)
    pprint(make_current_month_shift(current_date,15))