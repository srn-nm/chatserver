import socket
from threading import Thread, Lock
import json
import bcrypt
from groups_users import Group, User
from chatserver import ChatServer


if __name__ == "__main__":
    print("in server")
    server = ChatServer()
    server.listen()
    server.accept_connections()
