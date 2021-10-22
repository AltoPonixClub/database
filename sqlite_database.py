# https://www.sqlitetutorial.net/sqlite-python/

import sqlite3
from sqlite3 import Error
import pandas as pd

database_path = "./sqlite_database.db"

'''
To View Database:

sqlite3 sqlite_database.db
    If sqlite3 command not working, install: brew install sqlite3 or sudo apt install sqlite3

.tables: to view tables

'''

sql_command = """
                create table if not exists database (
                    id integer primary key,
                    name text not null,
                    begin_date text,
                    end_date text
                 );
               """


def connect(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def init(conn, command):
    try:
        c = conn.cursor()
        c.execute(command)
    except Error as e:
        print(e)
def things(conn):
    conn.execute("insert into database values (?, ?, ?, ?)", (1, "Hello", "a", "b"))
    conn.commit()
    print(pd.read_sql_query("select * from database", conn))
if __name__ == '__main__':
    conn = connect(database_path)
    init(conn, sql_command)
    things(conn)

