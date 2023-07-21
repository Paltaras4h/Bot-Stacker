import os
import mysql.connector
import json
from Models.User import User

db_config = None
db_url = None
try:
    with open(os.getcwd()+'/venv/configuration.json') as f:
        data = json.load(f)
        config = data['dataBaseConfig']
except FileNotFoundError:
    print("Configuration file not found, trying to access environment variables...")
    db_url = os.environ.get("CLEARDB_DATABASE_URL")
    user_pass, host_port_db = db_url.split("://")[1].split("@")
    username, password = user_pass.split(":")
    host_port, database = host_port_db.split("/")
    if ":" in host_port:
        hostname, port = host_port.split(":")
    else:
        hostname, port = host_port, 3306

    config = {
        "user": username,
        "password": password,
        "host": hostname,
        "port": int(port),
        "database": database.split("?")[0]
    }

# connection
def connect_to_data_base(autoCommit = True):# Connect to the MySQL database
    if config:
        cnx = mysql.connector.connect(**config)
    else:
        raise ValueError("No database configuration")
    cnx.autocommit = autoCommit
    return cnx

def get_connection(cnx, auto_commit = True):
    if cnx:
        return cnx, False
    else:
        return connect_to_data_base(auto_commit), True
# inserts
def insert_user(user, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO user (Id_User, User_Name) VALUES(%s, %s);", (str(user.id),user.name))
    if closeable: cnx.close()

def add_user_to_stack(user, stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM user_stack WHERE US_Id_User = %s AND US_Id_Stack = %s", (user.id, stack.id))
        if len(cur.fetchall()) == 0:
            cur.execute("INSERT INTO user_stack VALUES(%s, %s);", (user.id, stack.id))
        else:
            raise ValueError("Куда ээ, user already participates in the stack")
    if closeable: cnx.close()

def create_stack(stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO stack (Stack_Name, Lifetime_From, Lifetime_To) VALUES(%s, %s, %s);",
                    (stack.name, stack.lifetime_from, stack.lifetime_to))
        cur.execute("SELECT LAST_INSERT_ID();")
        stack_id = cur.fetchall()[0][0]
    if closeable: cnx.close()
    return stack_id

def insert_server(server, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO server VALUES(%s, %s, %s);",
                    (server.id, server.name, server.bot_chat_id))
    if closeable: cnx.close()
    return server.id

#updates
def update_user(user, cnx = None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("UPDATE user SET User_Name = %s, Last_Timestamp_From = %s, Last_Timestamp_To = %s, UTC = %s"
                            " WHERE Id_User = %s;",
                    (user.name, user.default_time_from, user.default_time_to, user.UTC, user.id))
    if closeable: cnx.close()

def update_stack(stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute(
            "UPDATE stack SET Stack_Name = %s, Lifetime_From = %s, Lifetime_To = %s WHERE Id_Stack = %s;",
            (stack.name, stack.lifetime_from, stack.lifetime_to, stack.id))
    if closeable: cnx.close()

def update_server(server, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute(
            "UPDATE server SET Name = %s, Bot_Chat_Id = %s WHERE Id_Server = %s;",
            (server.name, server.bot_chat_id, server.id))
    if closeable: cnx.close()

#deletes
def remove_user_from_stack(user_id, stack_id, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("DELETE FROM user_stack WHERE US_Id_User = %s AND US_Id_Stack = %s;",
                    (user_id,stack_id))
    if closeable: cnx.close()

def remove_user_from_stacks(user_id, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("DELETE FROM user_stack WHERE US_Id_User = %s;",
                    (user_id, ))
    if closeable: cnx.close()

def delete_stack(stack, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("DELETE FROM stack WHERE Id_Stack = %s;",
                    (stack.id,))
    if closeable: cnx.close()

#selects
def get_all_stacks(cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM stack")
        stacks_info = cur.fetchall()
    if closeable: cnx.close()
    return stacks_info

def select_user(user_id, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM user WHERE Id_User = %s;", (user_id,))
        users = cur.fetchall()
    if closeable: cnx.close()
    if len(users)==0:
        return None
    else:
        return users[0]

def get_participants_in_stack(stack_id, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM user INNER JOIN user_stack ON Id_User = US_Id_User WHERE US_Id_Stack = %s",(stack_id,))
        users_info = cur.fetchall()
    if closeable: cnx.close()
    return users_info

def select_server(server_id, cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM server WHERE Id_Server = %s",
                    (server_id,))
        server_info = cur.fetchall()
        if server_info:
            server_info = server_info[0]
        else:
            server_info = None
    if closeable: cnx.close()
    return server_info

def select_all_participants(cnx=None):
    cnx, closeable = get_connection(cnx)
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM user INNER JOIN user_stack ON Id_User = US_Id_User")
        users_info = cur.fetchall()
    if closeable: cnx.close()
    return users_info