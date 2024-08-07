import socket
import queue
import threading
import json
from messages import get_input, send_messages, receive_messages 

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1658



if __name__ == "__main__":
    msg_queue = queue.Queue()
    input_thread = threading.Thread(target=get_input, args=(msg_queue,))
    input_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        send_thread = threading.Thread(target=send_messages, args=(s, msg_queue,))
        send_thread.start()

        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

    input_thread.join()

    username = input("Username: ")
    password = input("Password: ")
    s.sendall(json.dumps({"username": username, "password": password}).encode())

    while True:
        try:
            command = input("Enter command (send, list_users, quit): ")
            if command == "send":
                continue
            elif command == "list_users":
                s.sendall(json.dumps({"type": "list_users"}).encode())
            elif command == "quit":
                break
            else:
                print("Invalid command")
        except KeyboardInterrupt:
            break