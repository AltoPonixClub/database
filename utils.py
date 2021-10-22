import pandas as pd
# def set(conn, variable, value):

def insert(conn):
    conn.execute("INSERT INTO database VALUES (?, ?, ?)", ("Bye", "a", "b"))
    conn.commit()
    # conn.execute("INSERT INTO database()", values)
    # conn.commit()

def to_string(conn):
    return (pd.read_sql_query("SELECT * FROM database", conn))

