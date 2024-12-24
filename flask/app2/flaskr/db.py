import pymongo

from flask import current_app, g


def get_db():
    if 'db' not in g:
        print("registramos una conexión")
        #current_app.config['DATABASE']
        dbClient = pymongo.MongoClient("mongodb+srv://appUser:matias123@cluster0.g2znx.gcp.mongodb.net/?retryWrites=true&w=majority")
        dbName="mydatabase"
        db = dbClient[dbName]
        g.db=db
            

    return g.db