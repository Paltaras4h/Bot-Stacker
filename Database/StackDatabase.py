import os
import mysql.connector
import json
from Models.User import User

with open(os.getcwd()+'/venv/configuration.json') as f:
    data = json.load(f)

config = data['dataBaseConfig']

def ConnectToDataBase(autoCommit = True):# Connect to the MySQL database
    cnx = mysql.connector.connect(**config)
    cnx.autocommit = autoCommit
    return cnx

def select_user(user_id):
    cnx = ConnectToDataBase()
    with cnx.cursor() as cur:
        cur.execute("SELECT * FROM user WHERE Id_User = %s;", (user_id,))
        users = cur.fetchall()
    cnx.close()
    if len(users)==0:
        return None
    else:
        return users[0]

def insert_user(user):
    cnx = ConnectToDataBase()
    with cnx.cursor() as cur:
        cur.execute("INSERT INTO user (Id_User, User_Name) VALUES(%s, %s);", (str(user.id),user.name))
    cnx.close()

def update_user(user):
    cnx = ConnectToDataBase()
    with cnx.cursor() as cur:
        cur.execute("UPDATE user SET (Id_User, User_Name, Last_Timestamp_From, Last_Timestamp_To",
                    (user.id, user.name, user.default_time_from, user.default_time_to))
    cnx.close()

def add_user_to_stack(user, stack):
    pass
def remove_user_from_stack(user,stack):
    pass
def delete_stack(utack):
    pass