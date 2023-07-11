import discord


class User:
    def __init__(self, id_in, name_in):
        self.user_id = id_in
        self.user_name = name_in
        self.default_time_from = None
        self.default_time_to = None

    def set_time_frame(self, time_from_in, time_to_in):
        self.default_time_from = time_from_in
        self.default_time_to = time_to_in

    @staticmethod
    def get_user(id_in, name_in):
        return None
