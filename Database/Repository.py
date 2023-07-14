import Database.StackDatabase as db
from Models.User import User
from Models.Stack import Stack
from datetime import datetime, timedelta

def normalize_time(time):
    if not time:
        return None
    now = datetime.now()
    time = now.replace(hour=time.hour, minute=time.minute)
    if time.replace(second=0, microsecond=0) < now.replace(second=0, microsecond=0):
        time += timedelta(days=1)
    return time

def set_user_time_frame(user, time_from, time_to, UTC=None):
    if type(time_from) != datetime or type(time_to) != datetime:
        raise TypeError("Об'єкт Datetime передавай в time_from й time_to, уася")

    user.default_time_from = normalize_time(time_from)
    user.default_time_to = normalize_time(time_to)
    if UTC:
        user.UTC = UTC
    db.update_user(user)
    return user

def set_stack_time_frame(stack, time_from, time_to):
    stack.lifetime_from = time_from
    stack.lifetime_to = time_to
    db.update_stack(stack)
    return stack

def get_user(id, name):
    """creates if does not exist"""
    cnx = db.connect_to_data_base(False)
    user = db.select_user(id, cnx=cnx)
    if user:
        _user = User(id, name, normalize_time(user[2]), normalize_time(user[3]), user[4])
        db.update_user(_user, cnx=cnx)
    else:
        _user = User(id, name)
        db.insert_user(_user, cnx=cnx)

    cnx.commit()
    cnx.close()
    return _user

def create_stack(user):
    """----------------------------------\n
    Creates a stack and adds user to it\n
    ----------------------------------\n
    Returns Stack object"""
    cnx = db.connect_to_data_base(False)
    stack = Stack(user.name, user.default_time_from, user.default_time_to)
    stack_id = db.create_stack(stack, cnx=cnx)
    stack.id = stack_id
    db.add_user_to_stack(user, stack, cnx=cnx)
    cnx.commit()
    cnx.close()
    return stack

def add_user_to_stack(user, stack):
    db.add_user_to_stack(user, stack)

def remove_user_from_stack(user, stack):
    db.remove_user_from_stack(user,stack)

def remove_stack(stack):
    db.delete_stack(stack)

def get_stacks():
    return [Stack(row[0], row[1], row[2], row[3]) for row in db.get_all_stacks()]