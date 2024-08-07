class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.groups = set()
        self.is_online = False

class Group:
    def __init__(self, name, creator):
        self.name = name
        self.members = {creator}

    def add_user(self, username):
        self.members.add(username)

    def remove_user(self, username):
        if username in self.members:
            self.members.remove(username)
