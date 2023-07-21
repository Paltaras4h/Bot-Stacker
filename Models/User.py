class User:
    def __init__(self, id:int, name, default_time_from=None, default_time_to=None, UTC=None):
        self.id = id
        self.name = name
        self.default_time_from = default_time_from
        self.default_time_to = default_time_to
        self.UTC = UTC
        