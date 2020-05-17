import errors
import os
import sqlite3 as db


class Database():

    DB_FILENAME = './gooey.db'

    def __init__(self):
        if not os.path.exists(self.DB_FILENAME):
            raise DbNotImplemented

        self.connection = db.connect(self.DB_FILENAME)

    def connection(self):
        if not self.connection_is_open():
            self.connection = db.connect(self.DB_FILENAME)
        
        return self.connection

    def close(self):
        return self.connection.close()

    def connection_is_open(self):
        for proc in psutil.process_iter():
            try:
                files = proc.get_open_files()
                if files:
                    for _file in files:
                        if _file.path == path:
                            return True    
            except psutil.NoSuchProcess as err:
                logging.error(err)
        return False
