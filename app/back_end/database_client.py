from getpass import getpass
from typing import Callable

from pymongo import MongoClient
from pymongo.database import Database

Dependency = Callable[[], Database]


class DBClient:

    def __init__(self) -> None:
        username = input('MongoDB username: ')
        password = getpass(prompt='MongoDB password: ')
        self.mongo_client = MongoClient(host='localhost',
                                        port=27017,
                                        username=username,
                                        password=password,
                                        authSource='admin',
                                        authMechanism='SCRAM-SHA-256')

    def get_db_dependency(self, db: str = '2048Infinite') -> Dependency:
        def dependency() -> Database:
            return self.mongo_client[db]

        return dependency


db_client = DBClient()
get_db = db_client.get_db_dependency()
