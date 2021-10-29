import pandas as pd
import json
import time

table_typings = None

# IMPORTANT:
# Only use ? params when creating sql commands
# Don't use any strine replacement methods, which will result in the possibility of sql injection
# ? params automatically escape inputs
# https://stackoverflow.com/questions/29528511/python-sqlite3-sql-injection-vulnerable-code


def current_milli_time():
    return round(time.time() * 1000)


def init(conn):
    conn.executescript('''
        CREATE TABLE if not exists monitors (
            id char(32) PRIMARY KEY NOT NULL,
            atmospheric_temp TEXT,
            reservoir_temp TEXT,
            light_intensity TEXT,
            soil_moisture TEXT,
            electrical_conductivity TEXT,
            ph TEXT,
            dissolved_oxygen TEXT,
            air_flow TEXT,
            foliage_feed TEXT,
            root_stream TEXT,
            CHECK(length(id) == 32 and TYPEOF(id) == 'text')
        );
    ''')
    conn.executescript('''
        CREATE TABLE if not exists owners (
            monitor_id char(32) PRIMARY KEY NOT NULL,
            user_id char(32) NOT NULL,
            CHECK(length(user_id) == 32 and TYPEOF(user_id) == 'text' and length(monitor_id) == 32 and TYPEOF(monitor_id) == 'text')
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


def update_monitor(conn, val):
    s = current_milli_time()
    j = get_monitors(conn, val["id"])
    l = []
    for i in j.items():
        if i[0] in val and i[0] != "id":
            if isinstance(i[1], dict) and isinstance(
                    val[i[0]], int) or isinstance(val[i[0]], float):
                try:
                    i[1]["value"] = float(val[i[0]])
                    i[1]["history"][str(s)] = float(val[i[0]])
                    l.append((i[0], json.dumps(i[1])))
                except BaseException:
                    pass
            if isinstance(i[1], str):
                l.append((i[0], val[i[0]]))
    if len(l) == 0:
        return {"success": False, "cause": "Invalid data"}, 400
    cur = conn.cursor()
    sql = "UPDATE monitors SET "
    data = []
    for i in l:
        if i[0] != "id":
            sql += i[0] + " = ?,"
            data.append(i[1])
    sql = sql[:-1] + " WHERE id = ?"
    data.append(val["id"])
    try:
        cur.execute(sql, tuple(data))
        conn.commit()
    except BaseException:
        return {"success": False, "cause": "Invalid data"}, 400


def to_string(conn):
    return (pd.read_sql_query("SELECT * FROM monitors", conn))


def sqltojson(s):
    json = {}
    for a in s:
        a = list(a)
        k = a.pop(0)
        t = ({table_typings[i + 1]: optionaljson(a[i])
             for i in range(len(table_typings) - 1)})
        if len(s) == 1:
            return t
        else:
            json[k] = t
    return json


def get_monitors(conn, key=None):
    cur = conn.cursor()
    if key is not None:
        cur.execute("SELECT * FROM monitors WHERE id = ?", (key,))
    else:
        cur.execute("SELECT * FROM monitors")
    v = cur.fetchall()
    return sqltojson(v)


def get_owners(conn, key=None):
    cur = conn.cursor()
    if key is not None:
        cur.execute(
            "SELECT monitors.id FROM owners JOIN monitors ON monitors.id = owners.monitor_id WHERE user_id = ?",
            (key,
             ))
        v = cur.fetchall()
        return [x[0] for x in v]
    else:
        cur.execute("SELECT * FROM owners")
        v = cur.fetchall()
        s = {}
        for a in v:
            if a[1] not in s:
                s[a[1]] = []
            s[a[1]].append(a[0])
        return s


def add_monitor(conn, val):
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO owners VALUES (?, ?)", val)
        cur.execute("""INSERT INTO monitors VALUES (?,
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '{"value":null,"history":{}}',
            '',
            ''
        )
        """, (val[0],))
        conn.commit()
    except Exception as e:
        if str(e).startswith("CHECK constraint failed"):
            return {"success": False, "cause": "Invalid id"}, 400
        if str(e).startswith("UNIQUE constraint failed"):
            return {"success": False, "cause": "monitor_id already exists"}, 400
        return {"success": False, "cause": "Unknown Error"}, 400


def reset_monitor(conn, id):
    if len(get_monitors(conn, id)) == 0:
        return {"success": False, "cause": "Invalid id"}, 400
    cur = conn.cursor()
    try:
        cur.execute("""UPDATE monitors SET
            atmospheric_temp = '{"value":null,"history":{}}',
            reservoir_temp = '{"value":null,"history":{}}',
            light_intensity = '{"value":null,"history":{}}',
            soil_moisture = '{"value":null,"history":{}}',
            electrical_conductivity = '{"value":null,"history":{}}',
            ph = '{"value":null,"history":{}}',
            dissolved_oxygen = '{"value":null,"history":{}}',
            air_flow = '{"value":null,"history":{}}',
            foliage_feed = '',
            root_stream = ''
            WHERE id = ?
        """, (id,))
        conn.commit()
    except Exception as e:
        if str(e).startswith("CHECK constraint failed"):
            return {"success": False, "cause": "Invalid id"}, 400
        if str(e).startswith("UNIQUE constraint failed"):
            return {"success": False, "cause": "monitor_id already exists"}, 400
        return {"success": False, "cause": "Unknown Error"}, 400


def delete_monitor(conn, id):
    if len(get_monitors(conn, id)) == 0:
        return {"success": False, "cause": "Invalid id"}, 400
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM owners WHERE monitor_id = ?", (id,))
        cur.execute("DELETE FROM monitors WHERE id = ?", (id,))
        conn.commit()
    except Exception as e:
        print(e)
        return {"success": False, "cause": "Unknown Error"}, 400


def optionaljson(v):
    try:
        return json.loads(v)
    except BaseException:
        return v
