import socket
from threading import Thread
import tkinter
from tkinter import *

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            message_list.insert(tkinter.END, message)
        except Exception:
            print("An error occured while receiving the message")

def send():
    message = my_message.get()
    my_message.set("")
    client.send(bytes(message, "utf8"))

window = Tk()
window.title("Chat room")
window.configure(bg="white")

message_frame = Frame(window, height=100, width=100, bg="white")
message_frame.pack()

my_message = StringVar()
my_message.set("")

scroll_bar = Scrollbar(message_frame)
message_list = Listbox(message_frame, height=15, width=100, bg="white", yscrollcommand=scroll_bar.set)
scroll_bar.pack(side=RIGHT, fill=Y)
message_list.pack(side=LEFT, fill=BOTH)
message_list.pack()

entry_field = Entry(window, textvariable=my_message, fg="black", width=50)
entry_field.pack()

send_button = Button(window, text="Send", font="Aerial", fg="white", bg="black", command=send)
send_button.pack()

host = "localhost"
port = 2000

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
client.connect((host, port))
print("Connected to server")

receive_thread = Thread(target=receive)
receive_thread.start()

mainloop()