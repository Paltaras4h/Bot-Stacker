import Database.StackDatabase as db
from Models.User import User
from Models.Stack import Stack
from datetime import datetime, timedelta

def normalize_time(time):
    """:param time datetime with correct hours and minutes
    :return: datetime with today's date and time's time"""
    if not time:
        return None
    now = datetime.now()
    time = now.replace(hour=time.hour, minute=time.minute)
    if time.replace(second=0, microsecond=0) < now.replace(second=0, microsecond=0):
        time += timedelta(days=1)
    return time.replace(second=0, microsecond=0)

def set_user_time_frame(user, time_from, time_to, UTC=None):
    """:param user: User object with correct id
    :param time_from: Datetime object with correct time (date is not required)
    :param time_to: Datetime object with correct time (date is not required)
    :param UTC: *Optional int object for setting user's UTC
        :return: Updated User object"""
    if type(time_from) != datetime or type(time_to) != datetime:
        raise TypeError("Об'єкт Datetime передавай в time_from й time_to, уася")

    user.default_time_from = normalize_time(time_from)
    user.default_time_to = normalize_time(time_to)
    if UTC:
        if type(UTC)!=int:
            raise TypeError("Об'єкт int передавай в UTC, уася")
        else:
            user.UTC = UTC
    db.update_user(user)
    return user

def set_stack_time_frame(stack, time_from, time_to):
    """:param stack: Stack object with correct id
        :param time_from: Datetime object with correct time (date is not required)
        :param time_to: Datetime object with correct time (date is not required)
            :return: Updated Stack object"""
    if type(time_from) != datetime or type(time_to) != datetime:
        raise TypeError("Об'єкт Datetime передавай в time_from й time_to, уася")
    stack.lifetime_from = time_from
    stack.lifetime_to = time_to
    db.update_stack(stack)
    return stack

def get_user(id, name=None):
    """
    :param id: str, int64 or snowflake: user id
    :param name: *Optional str: user name
    :returns: User object with all attributes from database if user exists in database by id OR New User object with timestamps and UTC set to None
    Note: Updates username if user exists in database"""
    cnx = db.connect_to_data_base(False)
    user = db.select_user(id, cnx=cnx)
    if user:
        _user = User(id, name if name else user[1], normalize_time(user[2]), normalize_time(user[3]), user[4])
        db.update_user(_user, cnx=cnx)
    else:
        _user = User(id, name)
        db.insert_user(_user, cnx=cnx)

    cnx.commit()
    cnx.close()
    return _user

def create_stack(user):
    """
    Creates a stack and adds user to it. Adds User timestamps to Stack timestamps.\n
    :returns: Stack object"""
    cnx = db.connect_to_data_base(False)
    stack = Stack(user.name, user.default_time_from, user.default_time_to)
    stack_id = db.create_stack(stack, cnx=cnx)
    stack.id = stack_id
    db.add_user_to_stack(user, stack, cnx=cnx)
    cnx.commit()
    cnx.close()
    return stack

def add_user_to_stack(user, stack):
    """
    :param user: User object with timestamps and UTC
    :param stack: Stack object: should be created using create_stack(user) func
    :return: None
    """
    if user.default_time_to and user.default_time_from and user.UTC:
        db.add_user_to_stack(user, stack)
    else:
        raise ValueError("User have no timestamps or UTC")

def remove_user_from_stacks(user):
    """
    Removes the passed user from all stacks where the user is currently in
    :param user: int or User: user id or User object with a correct id
    :return: None
    """
    if type(user) == User:
        db.remove_user_from_stacks(user.id)
    else:
        db.remove_user_from_stacks(user)

def remove_stack(stack):
    """
    Removes passed stack from database
    :param stack: Stack object
    :return: None
    """
    db.delete_stack(stack)

def get_stacks():
    """
    :return: A list of Stack objects that are currently in database
    """
    return [Stack(row[0], row[1], row[2], row[3]) for row in db.get_all_stacks()]

def get_participants(stack):
    """
    :param stack: Stack object with id existing in database
    :return: A list of User objects that are participating in passed stack
    """
    return [User(row[0], row[1], row[2], row[3], row[4]) for row in db.get_participants_in_stack(stack.id)]

