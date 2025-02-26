import socket
from threading import Thread

# Defines IP and port for server.
host = "localhost"
port = 2000

# Logs clients into a dictionary. 
clients = {}

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))

def handle_clients(connection):
    name = connection.recv(1024).decode()
    welcome_message = f"Welcome {name} to our chat room!"
    connection.send(bytes(welcome_message, "utf8"))
    message = name + " has recently joined the chat room."
    broadcast(bytes(message, "utf8"))

    clients[connection] = name

    while True:
        message = connection.recv(1024)
        broadcast(message, name + ":")

def broadcast(message, prefix=""):
    for client in clients: 
        client.send(bytes(prefix, "utf8") + message)

def accept_client_connection():
    while True:
        client_connection, client_address = server.accept()
        print(client_address, " has connected")

        client_connection.send(bytes("Welcome to the chat room. Enter your name to continue", "utf8"))
        Thread(target=handle_clients, args=(client_connection,)).start()

if __name__ == "__main__":
    server.listen(3)
    print("listening on port : ", port, "...")

    requests = Thread(target=accept_client_connection)

    requests.start()
    requests.join()
