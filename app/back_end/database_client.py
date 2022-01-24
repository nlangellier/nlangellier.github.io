from getpass import getpass
from typing import Callable

from pymongo import MongoClient
from pymongo.database import Database

Dependency = Callable[[], Database]


class DBClient:
    """
    Class to contain a MongoDB client and create database dependencies.
    """

    def __init__(self) -> None:
        """
        Logs into a MongoDB client and instantiates an instance of DBClient.
        """

        username = input('MongoDB username: ')
        password = getpass(prompt='MongoDB password: ')
        self.mongo_client = MongoClient(host='localhost',
                                        port=27017,
                                        username=username,
                                        password=password,
                                        authSource='admin',
                                        authMechanism='SCRAM-SHA-256')

    def get_db_dependency(self, db: str = '2048Infinite') -> Dependency:
        """
        Creates a database dependency to be used in path operation functions.

        Args:
            db (str): The name of the database to be accessed in the
                dependency.

        Returns:
            Dependency: A function that returns a PyMongo database object.
        """

        def dependency() -> Database:
            """
            Returns a PyMongo database object.

            Returns:
                Database: The database object.
            """

            return self.mongo_client[db]

        return dependency


db_client = DBClient()
get_db = db_client.get_db_dependency()
