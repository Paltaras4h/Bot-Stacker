import Database.StackDatabase as db
from Models.User import User
from Models.Stack import Stack

def set_user_time_frame(user):
    db.update_user(user)

def get_user(id, name):
    """creates if does not exist"""
    user = db.select_user(id)
    if user:
        _user = User(id, name, user[2], user[3])
        if _user.name != user[1]:
            db.update_user(_user)
        return _user
    else:
        _user = User(id, name)
        db.insert_user(_user)
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

def remove_user_from_stack(user):
    pass

def remove_stack():
    pass

def calculate_lifetime():
    pass