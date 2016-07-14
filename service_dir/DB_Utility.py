from pymongo import MongoClient

class Const:
    DB_HOST = 'localhost'
    DB_PORT = 27019
    DB_NAME = 'test'


def connet_db():
    client = Mongoclient(Const.DB_HOST, Const.DB_PORT)
    db = client[Const.DB_NAME]
    return client, db


def find(db, table, match = None, project = None, nosql = None):
    if match:
        rs = list(db[table].find([match, project]))
    else:
        rs = list(db[table].aggregate(nosql))
    return rs


def create
