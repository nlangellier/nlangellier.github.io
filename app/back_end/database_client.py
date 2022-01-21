from getpass import getpass

from pymongo import MongoClient

username = input('MongoDB username: ')
password = getpass(prompt='MongoDB password: ')
mongo_client = MongoClient(host='localhost',
                           port=27017,
                           username=username,
                           password=password,
                           authSource='admin',
                           authMechanism='SCRAM-SHA-256')
db = mongo_client['2048Infinite']
