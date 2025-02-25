import socket

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 2000

# Connect to server
client.connect((host, port))
print("Connected to server")

# Send messages and receive responses
while True:
    msg = input("Enter message: ")
    if not msg:
        break
    client.send(msg.encode())
    response = client.recv(1024).decode()
    print(f"Server says: {response}")

client.close()