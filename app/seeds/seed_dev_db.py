import json
from getpass import getpass
from pathlib import Path

from pymongo import MongoClient


def main():
    username = input('MongoDB username: ')
    password = getpass(prompt='MongoDB password: ')
    mongo_client = MongoClient(host='localhost',
                               port=27017,
                               username=username,
                               password=password,
                               authSource='admin',
                               authMechanism='SCRAM-SHA-256')
    db = mongo_client['2048Infinite']
    delete_result = db.leaderBoard.delete_many(filter={})
    print(f'Database clearing status: {delete_result.raw_result}')

    fpath_seed_data = Path(__file__).parent / 'devLeaderBoard.json'
    with open(file=fpath_seed_data, mode='r') as file_pointer:
        seed_data = json.load(file_pointer)

    insert_many_result = db.leaderBoard.insert_many(documents=seed_data)
    print(f'Num of inserted documents: {len(insert_many_result.inserted_ids)}')


if __name__ == '__main__':
    main()
