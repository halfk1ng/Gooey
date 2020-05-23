import os
import sqlite3 as db


class Database():

    DB_PATH = { 
        'production': './gooey.db',
        'development': './gooey_dev.db',
        'test': './gooey_test.db'
    }

    def __init__(self):
        path = self.select_db_path()
        self.connection = db.connect(path)

    def close(self):
        self.connection.close()

    def select_db_path(self):
        if os.environ['ENVIRONMENT'] in self.DB_PATH.keys():
            return self.DB_PATH[os.environ['ENVIRONMENT']]
        else:
            return self.DB_PATH['test']
