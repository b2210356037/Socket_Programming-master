import datetime
import socket
from _thread import *
import threading

import sys
import socket
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QLocale
from interface_ui import Ui_MainWindow  # Your PyQt5 GUI file name
from firebaseInitialize import *
from dotenv import load_dotenv
from firebase_admin import firestore 

import datetime

print_lock = threading.Lock()
clients = []  # List of client sockets
clients_lock = threading.Lock()  # Lock for managing clients

# Function to send messages to clients
# Function to send messages to all clients
def send_to_all_clients(message):
    with clients_lock:
        if message == "exit":
            for client in clients:
                try:
                    client.close()
                except Exception as e:
                    print(f"Error closing client socket: {e}")
            print("Server shutting down")
            exit()
        else:
            for client in clients:
                try:
                    client.send(message.encode())
                except Exception as e:
                    print(f"Error sending message to client: {e}")
                    client.close()
                    remove(client)

            # Add the message to Firestore logs
            log_entry = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'log': f"Server: {message}"
            }

            # Get the current date as the document ID
            document_id = log_entry['date']

            # Reference to the document
            doc_ref = db.collection('logs').document(document_id)

            # Fetch the existing document
            doc = doc_ref.get()
            if doc.exists:
                # Document exists, update the existing log entry
                existing_data = doc.to_dict()
                existing_logs = existing_data.get('logs', [])
                existing_logs.append(log_entry['log'])
                doc_ref.update({
                    'logs': existing_logs
                })
            else:
                # Document does not exist, create a new document
                doc_ref.set({
                    'date': log_entry['date'],
                    'logs': [log_entry['log']]
                })

#remove clients
def remove(connection):
    with clients_lock:
        if connection in clients:
            clients.remove(connection)

# Thread function for handling client connections
def threaded(c, addr):
    with clients_lock:
        clients.append(c)
    while True:
        try:
            # Receiving data from client
            data = c.recv(1024)
            if not data:
                print(f'Bye {addr}')
                break

            message = f"Message from {addr}: {data.decode('utf-8')}"
            print(message)

            # Print size of the clients
            with clients_lock:
                print(f"Number of clients: {len(clients)}")

        except Exception as e:
            print(f"Error receiving data from {addr}: {e}")
            break
    remove(c)
    c.close()

#send messages from the server
def send_messages():
    while True:
        msg = input("Server: ")
        send_to_all_clients(msg)

def Main():
    host = ""
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as e:
        print(f"Socket binding error: {e}")
        return
    s.listen(5)
    print("Socket is listening")

    # Start a new thread for the server to send messages
    start_new_thread(send_messages, ())

    while True:
        try:
            c, addr = s.accept()  # Establish connection with client
            print('Connected to :', addr[0], ':', addr[1])

            # Start a new thread for each client
            start_new_thread(threaded, (c, addr))
        except Exception as e:
            print(f"Error accepting connections: {e}")
            break
    s.close()

if __name__ == '__main__':
    Main()
