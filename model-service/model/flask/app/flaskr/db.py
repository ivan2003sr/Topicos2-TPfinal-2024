import pymongo
from flask import current_app,g
def get_db():
    if 'db' not in g:
        dbClient = pymongo.MongoClient("mongodb://mongoadmin:secret@localhost:27017/")
        dbName="sas"
        db=dbClient[dbName]
        g.db = db
    return g.db