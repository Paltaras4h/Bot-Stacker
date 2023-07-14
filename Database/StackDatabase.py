import os
import mysql.connector
import json
from Models.User import User

with open(os.getcwd()+'/venv/configuration.json') as f:
    data = json.load(f)

config = data['dataBaseConfig']

def connect_to_data_base(autoCommit = True):# Connect to the MySQL database
    cnx = mysql.connector.connect(**config)
    cnx.autocommit = autoCommit
    return cnx

def get_connection(cnx, auto_commit = True):
    if cnx:
        return cnx, False
    else:
        return connect_to_data_base(auto_commit), True

def select_user(user_id, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM user WHERE Id_User = %s;", (user_id,))
        users = cur.fetchall()
    if closeable: cnx.close()
    if len(users)==0:
        return None
    else:
        return users[0]

def insert_user(user, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO user (Id_User, User_Name) VALUES(%s, %s);", (str(user.id),user.name))
    if closeable: cnx.close()

def update_user(user, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("UPDATE user SET User_Name = %s, Last_Timestamp_From = %s, Last_Timestamp_To = %s, UTC = %s"
                            " WHERE Id_User = %s;",
                    (user.name, user.default_time_from, user.default_time_to, user.UTC, user.id))
    if closeable: cnx.close()

def create_stack(stack, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO stack (Stack_Name, Lifetime_From, Lifetime_To) VALUES(%s, %s, %s);",
                    (stack.name, stack.lifetime_from, stack.lifetime_to))
        cur.execute("SELECT LAST_INSERT_ID();")
        stack_id = cur.fetchall()[0][0]
    if closeable: cnx.close()
    return stack_id

def add_user_to_stack(user, stack, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO user_stack VALUES(%s, %s);",
                    (user.id, stack.id))
    if closeable: cnx.close()

def remove_user_from_stack(user,stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("DELETE FROM user_stack WHERE US_Id_User = %s AND US_Id_Stack = %s;",
                    (user.id, stack.id))
    if closeable: cnx.close()

def delete_stack(stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("DELETE FROM stack WHERE Id_Stack = %s;",
                    (stack.id,))
    if closeable: cnx.close()

def update_stack(stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute(
            "UPDATE user SET User_Name = %s, Last_Timestamp_From = %s, Last_Timestamp_To = %s WHERE Id_User = %s;",
            (stack.name, stack.default_time_from, stack.default_time_to, stack.id))
    if closeable: cnx.close()

def get_all_stacks(cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM stack")
        stacks_info = cur.fetchall()
    if closeable: cnx.close()
    return stacks_info

