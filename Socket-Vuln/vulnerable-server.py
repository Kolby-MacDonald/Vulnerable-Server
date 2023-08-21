import socket
import pickle
import threading
from enum import Enum, auto
import re


all_clients = []  # Global memory for all connected clients.


class ResponseFlag(Enum):
    """Type control for username validation."""

    VALID = auto()
    INVALID = auto()


class ConnectionFlag(Enum):
    """Type control for connection conditions."""

    CONNECTED = auto()
    DISCONNECTED = auto()


def handle_client(client_socket):
    """Localized memory/execution space for each connected client"""

    try:
        # Update all connected clients of new connection.
        all_usernames = [client[0] for client in all_clients]
        client_socket.send(pickle.dumps(all_usernames))

        # Gaurentee a user chooses a unique and properly formatted username.
        unique_username = ResponseFlag.INVALID.name
        while unique_username != ResponseFlag.VALID.name:
            username = client_socket.recv(1024).decode()

            if re.match(r"^[a-zA-Z0-9]+$", username) is not None:

                if username.lower() not in all_usernames:
                    unique_username = ResponseFlag.VALID.name

            client_socket.send(unique_username.encode())

        # Create a current client and add them to connected clients.
        current_client = [username, client_socket]
        all_clients.append(current_client)
        print(f"{username} Connected.")

        # Update all connected clients of new connection.
        distribute_data(username, ConnectionFlag.CONNECTED.name)

        # Listen for data from clients
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            received_object = pickle.loads(data)
            distribute_data(username, received_object)

    except Exception:
        close_connection(client_socket, username=username)


def distribute_data(username, received_object):
    """Distrubute new data to all clients except the sender."""

    for client in all_clients:
        if client[0] != username:
            client[1].send(username.encode())
            client[1].send(pickle.dumps(received_object))


def close_connection(client_socket, username=None):
    """Close a client socket and update other users if necessary."""

    if username != None:
        distribute_data(username, ConnectionFlag.DISCONNECTED.name)
        print(f"{username} disconnected.")
        all_clients.remove([username, client_socket])
    client_socket.close()


# Configure and start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("localhost", 12345)
server_socket.bind(server_address)
server_socket.listen(5)

print("Server is online.")

while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
