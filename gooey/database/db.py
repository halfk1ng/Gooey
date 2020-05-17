import os
import sqlite3 as db


class Database():

    DB_FILENAME = './gooey.db'

    def __init__(self):
        self.connection = db.connect(self.DB_FILENAME)

    def close(self):
        self.connection.close()
