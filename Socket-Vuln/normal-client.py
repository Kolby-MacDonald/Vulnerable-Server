import socket
import pickle
import threading
from enum import Enum, auto
from colorama import init, Fore
import pyfiglet


class ResponseFlag(Enum):
    """Type control for username validation."""

    VALID = auto()
    INVALID = auto()


class ConnectionFlag(Enum):
    """Type control for connection conditions."""

    CONNECTED = auto()
    DISCONNECTED = auto()


def send_data():
    """Main thread endpoint to send messages as a client."""

    while True:
        data = input(Fore.GREEN + "You: ")
        if data.lower() == "/quit":  # Allow the user to gracefully exit
            client_socket.close()
            break
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)


def receive_data():
    """New thread location to receive messages from other clients"""

    try:
        while True:
            sender = client_socket.recv(1024).decode()
            data = pickle.loads(client_socket.recv(1024))
            if not data:
                raise ConnectionAbortedError

            if data == ConnectionFlag.CONNECTED.name:
                print(Fore.YELLOW + f"\r{sender.upper()} HAS CONNECTED.")
            elif data == ConnectionFlag.DISCONNECTED.name:
                print(Fore.RED + f"\r{sender.upper()} HAS DISCONNECTED.")
            else:
                print(Fore.BLUE + f"\r{sender}: {data}")

            print("", end=Fore.GREEN + f"\rYou: ")
    except ConnectionAbortedError or ConnectionResetError:
        print(Fore.RED + f"You have disconnected.\n{'='*52}")


# Text Colour Control
init(autoreset=True)

# Legacy banner
legacy_banner = f"""
{Fore.GREEN + "=" * 50}
{Fore.GREEN}||{" " * 10}{Fore.GREEN}\x1b[3mWelcome To\x1b[0m{" " * 26}{Fore.GREEN}||
{Fore.GREEN}||{Fore.MAGENTA}{" " * 10}| THE {Fore.RED}\x1b[9mHACKABLE\x1b[0m{Fore.MAGENTA} CHAT ROOM |{" " * 10}{Fore.GREEN}||
{Fore.GREEN}||{" " * 25}{Fore.GREEN}\x1b[3mBy Kolby M.\x1b[0m{" " * 10}{Fore.GREEN}||
{Fore.GREEN + "=" * 50}"""

ascii_banner = (
    f"{Fore.GREEN}{pyfiglet.Figlet(font='standard').renderText('HACKABLE CHATROOM')}"
)
try:
    ascii_art = pyfiglet.Figlet(font="standard")
    print(f"{Fore.RED}{'='*52}")
    print(f"{Fore.RED}\x1b[3mWelcome To The\x1b[0m\n")
    print(ascii_banner)
    print(f"{Fore.RED}{' '*41}\x1b[3mBy Kolby M.\x1b[0m")
    print(f"{Fore.RED}{'='*52}")

except:  # Some Figlet Error, print the legacy banner.
    print(legacy_banner)

try:
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 12345)
    client_socket.connect(server_address)

    connected_users = pickle.loads(client_socket.recv(1024))
    if not connected_users:
        print(Fore.MAGENTA + "It's just you, wait for more others to join.")
    else:
        taken_usernames = ",".join(connected_users)
        print(Fore.MAGENTA + f"TAKEN USERNAMES: {taken_usernames}")

    # Send username to the server and wait to see if it's unique.
    unique_username = ResponseFlag.INVALID.name
    while unique_username != ResponseFlag.VALID.name:
        username = input(Fore.GREEN + "Enter your username: ")
        client_socket.send(username.encode())

        unique_username = client_socket.recv(1024).decode()
        if unique_username != ResponseFlag.VALID.name:
            print(Fore.RED + "Invalid Username, try again.")

    # Get current users.
    print(f"""{Fore.MAGENTA}Welcome {username}, You can start chatting now.\n{Fore.RED + '='*52}""")

    # Start a thread to receive messages from other clients.
    receive_thread = threading.Thread(target=receive_data)
    receive_thread.start()

    # Set the main process to send messages as they're entered.
    send_data()
except:
    print(Fore.MAGENTA + "The server is offline. Try again later.\n")
