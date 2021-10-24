import pandas as pd

table_typings = None

# IMPORTANT:
# Only use ? params when creating sql commands
# Don't use any strine replacement methods, which will result in the possibility of sql injection
# ? params automatically escape inputs
# https://stackoverflow.com/questions/29528511/python-sqlite3-sql-injection-vulnerable-code


def init(conn):
    conn.executescript('''
        CREATE TABLE if not exists monitors (
            key char(32) PRIMARY KEY NOT NULL,
            atmospheric_temp DECIMAL(10,5),
            reservoir_temp DECIMAL(10,5),
            foliage_feed text
            CHECK(length(key) == 32 and TYPEOF(key) == 'text' and (TYPEOF(atmospheric_temp) == 'real' or TYPEOF(atmospheric_temp) == 'integer' or TYPEOF(atmospheric_temp) == 'null') and (TYPEOF(reservoir_temp) == 'real' or TYPEOF(reservoir_temp) == 'integer' or TYPEOF(reservoir_temp) == 'null') and (TYPEOF(foliage_feed) == 'text' or TYPEOF(foliage_feed) == 'null'))
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


def isolate_updatable(content):
    return {i[0]: i[1] for i in content.items(
    ) if i[0] in table_typings and i[1] is not None}


def update(conn, val):
    cur = conn.cursor()
    sql = "UPDATE monitors SET "
    data = []
    for i in val.items():
        if i[0] != "key":
            sql += i[0] + " = ?,"
            data.append(i[1])
    sql = sql[:-1] + " WHERE key = ?"
    data.append(val["key"])
    try:
        cur.execute(sql, tuple(data))
        conn.commit()
    except BaseException:
        return {"success": False, "cause": "Invalid data!"}, 400


def to_string(conn):
    return (pd.read_sql_query("SELECT * FROM monitors", conn))


def sqltojson(s):
    json = {}
    for a in s:
        a = list(a)
        k = a.pop(0)
        t = ({table_typings[i + 1]: a[i]
             for i in range(len(table_typings) - 1)})
        if len(s) == 1:
            return t
        else:
            json[k] = t
    return json


def get(conn, key=None):
    cur = conn.cursor()
    if key is not None:
        cur.execute("SELECT * FROM monitors WHERE key = ?", (key,))
    else:
        cur.execute("SELECT * FROM monitors")
    return sqltojson(cur.fetchall())
