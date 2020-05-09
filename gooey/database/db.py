import os
import sqlite3 as db

db_filename = './gooey.db'

db_is_new = not os.path.exists(db_filename)

conn = db.connect(db_filename)

if db_is_new:
    print('Need to create schema')
else:
    print('Database exists, assume schema does, too.')

conn.close()