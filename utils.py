import pandas as pd
import random
# def set(conn, variable, value):

def init(conn):
    try:
        with open("./sql_scripts/init.sql") as f:
            conn.executescript(f.read())
    except Exception as e:
        print(e)

def insert(conn):
    conn.execute("INSERT INTO database VALUES (?, ?, ?, ?)", (1, "Bye", 1, 2))
    conn.commit()
    # conn.execute("INSERT INTO database()", values)
    # conn.commit()
def set(conn):
    with open("./sql_scripts/set.sql") as f:
        template = f.read()
        # TODO: parameters
        command = template.replace("<id>", "1").replace("<reservoir_temp>", str(1)).replace("<foliage_feed>", "\'woahfeed\'").replace("<atmospheric_temp>", str(random.randint(0, 10)))
        conn.execute(command)

def to_string(conn):
    return (pd.read_sql_query("SELECT * FROM database", conn))

