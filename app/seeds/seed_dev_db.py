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

    dirpath_seed_data = Path(__file__).parent

    print('\nSeeding development database...')

    for collection in ['games', 'moveHistory', 'tileCreationHistory']:
        print(f'\nClearing {collection} collection...')
        delete_result = db[collection].delete_many(filter={})
        print(f'\tDeletion result: {delete_result.raw_result}')

        print(f'Inserting seed data to {collection} collection...')
        fpath_seed_data = dirpath_seed_data / f'dev_{collection}.json'
        with open(file=fpath_seed_data, mode='r') as file_pointer:
            seed_data = json.load(file_pointer)
        insert_many_result = db[collection].insert_many(documents=seed_data)
        num_documents = len(insert_many_result.inserted_ids)
        print(f'\tNumber of inserted documents: {num_documents}')

    print('\nSeeding complete.')


if __name__ == '__main__':
    main()
