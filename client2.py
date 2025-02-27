import socket
from threading import Thread
import tkinter
from tkinter import *

"""Function used to receive messages."""
def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            message_list.insert(tkinter.END, message)
        except Exception:
            print("An error occured while receiving the message.")

"""Function used to send messages."""
def send():
    message = my_message.get()
    my_message.set("")
    client.send(bytes(message, "utf8"))

# Creates the tkinter application.
window = Tk()
# Names the application.
window.title("Chat room")
# Color scheme.
window.configure(bg="white")

# This creates the box where the messages will exist and update.
message_frame = Frame(window, height=100, width=100, bg="white")
message_frame.pack()

# Creates a string variable for the user's message.
my_message = StringVar()
my_message.set("")

# Adds a scroll bar to view older messages in chat room. 
scroll_bar = Scrollbar(message_frame)
# Merges the frame and scroll bar together. 
message_list = Listbox(message_frame, height=15, width=100, bg="white", yscrollcommand=scroll_bar.set)
# Puts the scroll bar on the right side of the frame.
scroll_bar.pack(side=RIGHT, fill=Y)
message_list.pack(side=LEFT, fill=BOTH)
message_list.pack()

# Adds a box where the user can type messages that will be sent. 
entry_field = Entry(window, textvariable=my_message, fg="black", width=50)
entry_field.pack()

# Creates a button that will be used to send messages into the chat room. 
send_button = Button(window, text="Send", font="Aerial", fg="white", bg="black", command=send)
send_button.pack()

# IP address and port used to connect clients to the server. 
host = "localhost"
port = 2000

# Create a socket object.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server. 
client.connect((host, port))
print("Connected to server")

# Thread used to allow multiple client requests to the server at the same time. 
receive_thread = Thread(target=receive)
receive_thread.start()

"""This function is used to keep the tkinter function running until the application window is closed."""
mainloop()