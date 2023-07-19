import Database.StackDatabase as db
import discord
from Models.User import User
from Models.Stack import Stack
from Models.Server import Server
from datetime import datetime, timedelta, timezone

def normalize_timeframe(time_from, time_to):
    """:param time datetime with correct hours and minutes
    :return: datetime with today's date and time's time"""
    if not time_from or not time_to:
        return None
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0, tzinfo=None)
    time_from = now.replace(hour=time_from.hour, minute=time_from.minute, second=0, microsecond=0)
    time_to = now.replace(hour=time_to.hour, minute=time_to.minute, second=0, microsecond=0)
    if time_from < now and time_from+timedelta(days=1) < time_to:
        time_from += timedelta(days=1)
    if time_to < now and time_from < time_to+timedelta(days=1):
        time_to += timedelta(days=1)
    return time_from.replace(second=0, microsecond=0), time_to.replace(second=0, microsecond=0)

# creates
def create_stack(user):
    """
    Creates a stack and adds user to it. Adds User timestamps to Stack timestamps. Adds user to stack\n
    :returns: Stack object"""
    cnx = db.connect_to_data_base(False)
    stack = Stack(user.name, user.default_time_from, user.default_time_to)
    stack_id = db.create_stack(stack, cnx=cnx)
    stack.id = stack_id
    db.add_user_to_stack(user, stack, cnx=cnx)
    cnx.commit()
    cnx.close()
    return stack

#updates
def add_user_to_stack(user, stack):
    """
    :param user: User object with timestamps and UTC
    :param stack: Stack object: should be created using create_stack(user) func
    :return: None
    """
    cnx = db.connect_to_data_base(False)
    if user.default_time_to and user.default_time_from and user.UTC:
        db.add_user_to_stack(user, stack, cnx)

        stack.lifetime_from = max(user.default_time_from, stack.lifetime_from)
        stack.lifetime_to = min(user.default_time_to, stack.lifetime_to)
        db.update_stack(stack, cnx)
        cnx.commit()
        cnx.close()
    else:
        raise ValueError("User have no timestamps or UTC")

#deletes
def remove_user_from_stack(user, stack):
    cnx = db.connect_to_data_base(False)
    db.remove_user_from_stack(user.id, stack.id, cnx=cnx)
    parts_info = db.get_participants_in_stack(stack.id, cnx=cnx)
    if len(parts_info)<1:
        db.delete_stack(stack, cnx=cnx)
    cnx.commit()
    cnx.close()

def remove_user_from_stacks(user):
    """
    Removes the passed user from all stacks where the user is currently in
    :param user: int or User: user id or User object with a correct id
    :return: None
    """
    cnx = db.connect_to_data_base(False)
    if type(user) == User:
        db.remove_user_from_stacks(user.id,cnx=cnx)
    else:
        db.remove_user_from_stacks(user,cnx=cnx)
    for stack in db.get_all_stacks(cnx=cnx):
        parts_info = db.get_participants_in_stack(stack.id, cnx=cnx)
        if len(parts_info) < 1:
            db.delete_stack(stack, cnx=cnx)
    cnx.commit()
    cnx.close()

def remove_stack(stack):
    """
    Removes passed stack from database
    :param stack: Stack object
    :return: None
    """
    db.delete_stack(stack)

#setters
def set_user_time_frame(user, time_from, time_to, UTC=None):
    """:param user: User object with correct id
    :param time_from: Datetime object with correct time (date is not required)
    :param time_to: Datetime object with correct time (date is not required)
    :param UTC: *Optional int object for setting user's UTC
        :return: Updated User object"""
    if type(time_from) != datetime or type(time_to) != datetime:
        raise TypeError("Об'єкт Datetime передавай в time_from й time_to, уася")

    user.default_time_from, user.default_time_to = normalize_timeframe(time_from, time_to)
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

#getters
def get_user(id, name=None):
    """
    :param id: str, int64 or snowflake: user id
    :param name: *Optional str: user name
    :returns: User object with all attributes from database if user exists in database by id OR New User object with timestamps and UTC set to None
    Note: Updates username if user exists in database"""
    cnx = db.connect_to_data_base(False)
    user = db.select_user(id, cnx=cnx)
    if user:
        time_from, time_to = normalize_timeframe(user[2], user[3])
        _user = User(id, name if name else user[1], time_from, time_to, user[4])
        db.update_user(_user, cnx=cnx)
    else:
        _user = User(id, name)
        db.insert_user(_user, cnx=cnx)

    cnx.commit()
    cnx.close()
    return _user

def get_stacks():
    """
    :return: A list of Stack objects that are currently in database
    """
    return [Stack(row[1], row[2], row[3], id=row[0]) for row in db.get_all_stacks()]

def get_server(id, name=None, bot_chat_id=None):
    """
    Returns existing Server by id of creates new
    :param id: server id
    :param name: *server name: REQUIRED WHILE CREATING NEW SERVER
    :param bot_chat_id: * chat id where bot sends messages EQUIRED WHILE CREATING NEW SERVER
    :return: Models.Server object
    """
    cnx = db.connect_to_data_base(False)
    server_info = db.select_server(id, cnx=cnx)
    if server_info:
        server = Server(id, name if name else server_info[1], bot_chat_id if bot_chat_id else server_info[2])
        if name!=server_info[1] or bot_chat_id!=server_info[2]:
            db.update_server(server, cnx=cnx)
    else:
        if not name or not bot_chat_id:
            raise ValueError("To add a new server to database, name and bot_chat_id are required.")
        server = Server(id, name, bot_chat_id)
        db.insert_server(server, cnx=cnx)

    cnx.commit()
    cnx.close()
    return server

def get_participants(stack):
    """
    :param stack: Stack object with id existing in database
    :return: A list of User objects that are participating in passed stack
    """
    return [User(row[0], row[1], row[2], row[3], row[4]) for row in db.get_participants_in_stack(stack.id)]

def get_bot_channel(guild):
    server_info = db.select_server(guild.id)
    return discord.utils.get(guild.text_channels, id=int(server_info[2]))

def get_playing_users():
    return [User(record[0], record[1], record[2], record[3], record[4]) for record in db.select_all_participants()]

#bools
def user_participates_in(user, stack):
    for part in get_participants(stack):
        if part.id == str(user.id):
            return True
    return False
