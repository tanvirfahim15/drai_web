from pymongo import MongoClient
from threading import Lock


# Singleton Class
class Database:
    db = None
    instance = None
    lock = Lock()

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.doctorai


    @staticmethod
    def get_instance():
        Database.lock.acquire()
        if Database.instance is None:
            Database.instance = Database()
        Database.lock.release()
        return Database.instance


# loads singleton object for database to prevent multiple connections
db = Database.get_instance().db

