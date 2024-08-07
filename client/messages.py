import socket
import queue
import json

def get_input(queue: queue.Queue):
    while True:
        message_type = input("Enter message type (chat, private): ")
        if message_type not in ["chat", "private"]:
            print("Invalid message type")
            continue

        if message_type == "chat":
            content = input("Enter message: ")
            message = {"type": "chat", "content": content}
        else:
            recipient = input("Enter recipient: ")
            content = input("Enter message: ")
            message = {"type": "private", "recipient": recipient, "content": content}

        queue.put(message)

def send_messages(socket, queue: queue.Queue):
    while True:
        try:
            message = queue.get()
            if message != None:
                socket.sendall(json.dumps(message).encode())
                if message == "q":
                    break
        except queue.Empty:
            pass

def receive_messages(socket):
    while True:
        try:
            data = socket.recv(1024)
            if not data:
                break
            message = json.loads(data.decode())
            print(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break
