import socket
from threading import Thread, Lock
import json
import bcrypt
from groups_users import Group, User

class ChatServer:
    def __init__(self, host="127.0.0.1", port=1658):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.c = {}  
        self.u = {} 
        self.g = {}  
        self.l = Lock()

        self.register_user("user1", "password1")
        self.register_user("user2", "password2")

    def register_user(self, username, password):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.u[username] = User(username, password_hash)

    def listen(self):
        self.s.listen()

    def accept_connections(self):
        while True:
            try:
                c, a = self.s.accept()
                print(f"Client {a} connected.")
                t = Thread(target=self.handle_authentication, args=(c, a))
                t.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_authentication(self, c, a):
        try:
            data = c.recv(1024).decode()
            auth_data = json.loads(data)
            username = auth_data.get('username')
            password = auth_data.get('password')

            if username in self.u:
                user = self.u[username]
                if bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
                    with self.l:
                        self.c[a] = (c, user)
                        user.is_online = True
                        print(f"User {username} logged in.")
                        t = Thread(target=self.handle_client, args=(c, a, user))
                        t.start()
                else:
                    c.sendall(json.dumps({"error": "Incorrect password"}).encode())
            else:
                c.sendall(json.dumps({"error": "User not found"}).encode())
        except Exception as e:
            print(f"Error handling authentication: {e}")

    def handle_client(self, c, a, user):
        try:
            while True:
                data = c.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "chat":
                    self.broadcast({"type": "chat", "sender": user.username, "message": message["content"]})
                elif message_type == "private":
                    recipient = message.get("recipient")
                    recipient_socket, _ = self.get_user_socket(recipient)
                    if recipient_socket:
                        recipient_socket.sendall(json.dumps({"type": "private", "sender": user.username, "message": message["content"]}).encode())
                elif message_type == "group":
                    group_action = message.get("action")
                    group_name = message.get("group")

                    if group_action == "create":
                        if group_name not in self.g:
                            self.g[group_name] = Group(group_name, user.username)
                            user.groups.add(group_name)
                        else:
                            c.sendall(json.dumps({"error": "Group already exists"}).encode())
                    elif group_action == "join":
                        if group_name in self.g:
                            group = self.g[group_name]
                            group.add_user(user.username)
                            user.groups.add(group_name)
                        else:
                            c.sendall(json.dumps({"error": "Group not found"}).encode())
                    elif group_action == "leave":
                        if group_name in self.g:
                            group = self.g[group_name]
                            group.remove_user(user.username)
                            user.groups.remove(group_name)
                        else:
                            c.sendall(json.dumps({"error": "Group not found"}).encode())
                    elif group_action == "send":
                        if group_name in self.g:
                            group = self.g[group_name]
                            for member_username in group.members:
                                if member_username != user.username:  
                                    member_socket, _ = self.get_user_socket(member_username)
                                    if member_socket:
                                        member_socket.sendall(json.dumps({"type": "group", "group": group_name, "sender": user.username, "message": message["content"]}).encode())
                        else:
                            c.sendall(json.dumps({"error": "Group not found"}).encode())
                    else:
                        pass
                else:
                    pass
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            print(f"Client {a} disconnected.")
            if a in self.c:
                del self.c[a]
                user.is_online = False  

    def broadcast(self, m):
        with self.l:
            for c, u in self.c.items():
                try:
                    c.sendall(json.dumps(m).encode())
                except Exception as e:
                    print(f"Error broadcasting message: {e}")

    def get_user_socket(self, username):
        for a, (s, u) in self.c.items():
            if u.username == username:
                return s, a
        return None, None
