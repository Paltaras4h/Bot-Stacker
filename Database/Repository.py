import Database.StackDatabase as db
from Models.User import User

def set_user_time_frame(user):
    db.update_user(user)

def get_user(id, name):
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

def add_user(self, user):
    pass

def remove_user(self, user):
    pass

def remove_stack(self):
    pass

def calculate_lifetime(self):
    pass