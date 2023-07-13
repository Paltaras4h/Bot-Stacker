class Stack:
    def __init__(self, name, time_from, time_to, id=None):
        self.id = id
        self.name = name
        self.lifetime_from = time_from
        self.lifetime_to = time_to
