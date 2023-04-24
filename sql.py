import sqlite3
from datetime import datetime, timedelta

def db(db_str):
    con = sqlite3.connect('data.db')
    c = con.cursor()
    # print(db_str)
    c.execute(db_str)
    output = c.fetchall()
    con.commit()
    con.close()
    return output

# ----------------------------
# ------- General ------------
# ----------------------------

def db_create_table():
    db_str = "CREATE TABLE general(name TEXT, variable TEXT, value_text TEXT, value_float FLOAT)"
    db(db_str)

def db_delete_table(table):
    db_str = f"DROP TABLE {table}"
    db(db_str)

def db_update(name, variable, value, variable_type):
    condition = f" WHERE name='{name}' and variable = '{variable}'"
    db_str = f"SELECT * FROM general" + condition
    value_string, value_float = "", 0
    if variable_type == "string": value_string = value
    else: value_float = value
    if value_float is None: value_float = 0

    existing = len(db(db_str))
    if existing == 0:
        db(f"INSERT INTO general VALUES ('{name}', '{variable}', '{value_string}', {value_float})")
    else:
        db(f"UPDATE general SET value_text='{value_string}'" + condition)
        db(f"UPDATE general SET value_float={value_float}" + condition)

def db_read(name, variable):
    condition = f" WHERE name='{name}' and variable = '{variable}'"
    db_str = f"SELECT * FROM general" + condition
    result = db(db_str)
    if len(result) > 0:
        if result[0][2] != "": return result[0][2]
        else: return result[0][3]
    # Manage null responses
    if variable in ["map50", "map95"]: return 0
    # print("DB Read failure", name, variable)

def db_read_time(name, variable):
    # print(variable)
    result = db_read(name, variable)
    if result is None: return timedelta(minutes=0)
    t = datetime.strptime(result, "%H:%M:%S")
    delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    return delta

# ---------------------------------------
# ------- Calibration Points ------------
# ---------------------------------------

def db_create_table_calibration_point():
    db_str = "CREATE TABLE calibration_point(scene TEXT, x1 FLOAT, y1 FLOAT, x2 FLOAT, y2 FLOAT, x FLOAT, y FLOAT, z FLOAT)"
    db(db_str)

def db_write_calibration_point(scene, x1, y1, x2, y2, x, y, z):
    # Check if existing
    db_str = f"SELECT * FROM calibration_point WHERE scene='{scene}' and x1={x1} and y1={y1} and x2={x2} and y2={y2} and x={x} and y={y} and z={z}"
    if len(db(db_str)) == 0:
        # Write
        db(f"INSERT INTO calibration_point VALUES ('{scene}', {x1}, {y1}, {x2}, {y2}, {x}, {y}, {z})")

def db_read_calibration_points(scene):
    db_str = f"SELECT * FROM calibration_point WHERE scene='{scene}'"
    points = db(db_str)
    result = []
    for point in points:
        # scene, x1, y1, x2, y2, x, y, z = point
        result.append(point)
    # print(result)
    return result

def db_delete_calibration_point(scene, x1, y1, x2, y2, x, y, z):
    db_str = f"DELETE from calibration_point where scene='{scene}' and x1={x1} and y1={y1} and x2={x2} and y2={y2} and x={x} and y={y} and z={z})"
    db(db_str)

# ---------------------------
# ------- Scenes ------------
# ---------------------------

def db_create_table_scenes():
    db_str = "CREATE TABLE scenes(scene TEXT)"
    db(db_str)

def db_write_scenes(scene):
    db_str = f"SELECT * FROM scenes WHERE scene='{scene}'"
    if len(db(db_str)) == 0:
        db(f"INSERT INTO scenes VALUES ('{scene}')")

def db_read_scenes():
    return db("SELECT * FROM scenes")

def db_delete_calibration_point(scene, x1, y1, x2, y2, x, y, z):
    db_str = f"DELETE from calibration_point where scene='{scene}' and x1={x1} and y1={y1} and x2={x2} and y2={y2} and x={x} and y={y} and z={z})"
    db(db_str)


# ----------------------------
# ------- Other --------------
# ----------------------------

def db_read_all(table="general"):
    db_str = f"SELECT * FROM {table}"
    result = db(db_str)
    for x in result:
        print(x)

# ----------------------------
# ------- Set up -------------
# ----------------------------
def create_tables():
    db_create_table()
    db_create_table_calibration_point()
    db_create_table_scenes()

# create_tables()


# db_read_all("scenes")

# db_create_table_scenes()