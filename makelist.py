import random
import csv
from pprint import pprint
from typing import Union
from faker import Faker

def generate_unique_numbers(count:int):
    try:
        if count > 10000:
            raise ValueError("Count must be less than or equal to 10000")
        numbers:list[int] = list(range(10000))
        random.shuffle(numbers)
        return numbers[:count]
    except ValueError as e:
        print(f"Error: {e}")
        return []
    
def make_fake_data(count:int) -> list[dict[str,Union[str,int]]]:
    fake:Faker = Faker("ja-JP")
    num_list:list[int] = generate_unique_numbers(count) 

    datalist:list[dict[str,Union[str,int]]] = list()
    for i in range(count):
        datalist.append({
            "ID": num_list[i],
            "Name": fake.name(),
            "Address": fake.address()
        })
    return sorted(datalist,key=lambda x: x['ID'])

def make_csv(filepath:str,datalist:list[dict[str,Union[str,int]]]):
    try :
        with open(filepath,"w",encoding="UTF8",newline='') as f:
            writer = csv.DictWriter(f, fieldnames= datalist[0].keys())
            writer.writeheader()
            writer.writerows(datalist)
    except FileNotFoundError as e:
        print(f"Error: {e}")

                

# 例として、10個の数を抜き出す場合
if __name__ == "__main__":
    make_csv("./dummydata.csv",make_fake_data(1000))