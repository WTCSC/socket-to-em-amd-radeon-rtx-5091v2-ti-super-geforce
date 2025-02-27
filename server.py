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

"""Function used to handle clients that connect to the server."""
def handle_clients(connection):
    # Recovers an 8 bit message (the name of the client) and decodes it. 
    name = connection.recv(1024).decode()
    welcome_message = f"Welcome {name} to our chat room!"
    # Server sends a direct message to the client that has recently joined.
    connection.send(bytes(welcome_message, "utf8"))
    message = name + " has recently joined the chat room."
    # Used to display a message from the server to all clients. 
    # This broadcast message is who has recently joined the chat room. 
    broadcast(bytes(message, "utf8"))

    # Saves the clients name into the dictionary.
    clients[connection] = name

    while True:
        message = connection.recv(1024)
        broadcast(message, name + ":")

"""Function used to broadcast messages to all clients connected to the server."""
def broadcast(message, prefix=""):
    for client in clients: 
        client.send(bytes(prefix, "utf8") + message)

"""Function used to accept clients requesting to join the chat room."""
def accept_client_connection():
    while True:
        # Used to accept clients 
        client_connection, client_address = server.accept()
        print(client_address, " has connected")

        client_connection.send(bytes("Welcome to the chat room. Enter your name to continue", "utf8")) 
        # Starts multi-threading.
        Thread(target=handle_clients, args=(client_connection,)).start()

if __name__ == "__main__":
    # Allows up to 3 client connections to the server.
    server.listen(3)
    print("listening on port : ", port, "...")

    # Allows for the server to accept multiple requests at once. 
    requests = Thread(target=accept_client_connection)

    requests.start()
    requests.join()
