import discord
import db


class Stack:
    def __init__(self, name_in, time_from, time_to):
        self.id = db.create_stack(name_in)
        self.name = name_in
        self.lifetime_from = time_from
        self.lifetime_to = time_to

    def add_user(self, user):
        db.addUser()
        return db.get_users

    def remove_user(self, user):
        return db.get_users

    def remove_stack(self):
        return False

    def calculate_lifetime(self):
        return self.lifetime_from, self.lifetime_to
