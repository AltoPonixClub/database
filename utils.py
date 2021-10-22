import pandas as pd

table_typings = None

def init(conn):
    conn.executescript('''
        CREATE TABLE if not exists monitors (
            key char(32) PRIMARY KEY,
            foliage_feed text,
            atmospheric_temp float,
            reservoir_temp float
        );
    ''')
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(monitors)")
    global table_typings
    table_typings = [x[1] for x in cur.fetchall()]

def insert(conn, val):
    cur = conn.cursor()
    cur.execute("INSERT INTO monitors VALUES (?, ?, ?, ?)", val)
    conn.commit()

def update(conn, val):
    cur = conn.cursor()
    # put id last
    task = (val[1],val[2],val[3],val[0])
    sql = '''   UPDATE monitors 
                SET foliage_feed = ?,
		            atmospheric_temp = ?,
		            reservoir_temp = ?
                WHERE key = ?'''
    cur.execute(sql, task)
    conn.commit()

def to_string(conn):
    return (pd.read_sql_query("SELECT * FROM monitors", conn))

def sqltojson(s):
    json = {}
    for a in s:
        a = list(a)
        k = a.pop(0)
        t = ({table_typings[i+1]: a[i] for i in range(len(table_typings)-1)})
        if len(s)==1:
            return t
        else:
            json[k]=t
    return json

def get(conn, key=None):
    cur = conn.cursor()
    if key is not None:
        cur.execute("SELECT * FROM monitors WHERE key = ?",(key,))
    else:
        cur.execute("SELECT * FROM monitors")
    return sqltojson(cur.fetchall())
