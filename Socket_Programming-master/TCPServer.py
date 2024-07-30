import datetime
import re
import socket
from _thread import start_new_thread
import threading
from firebaseInitialize import *
from firebase_admin import firestore
from datetime import datetime

print_lock = threading.Lock()
clients = {}  # Dictionary to manage client sockets
clients_lock = threading.Lock()  # Lock for managing clients

# Function to send messages to a specific client
def send_client(message, target_ip):
    with clients_lock:
        # Find the client with the matching IP address
        target_client = None
        for addr, client_socket in clients.items():
            if addr[0] == target_ip:
                target_client = client_socket
                break
        
        if target_client:
            try:
                target_client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client {target_ip}: {e}")
                target_client.close()
                remove(target_client)
        else:
            print(f"No client found with IP address {target_ip}")

# Function to send messages to all clients
def send_to_all_clients(message):
    db = firestore.client()
    with clients_lock:
        if message == "exit":
            for addr, client in clients.items():
                try:
                    client.close()
                except Exception as e:
                    print(f"Error closing client socket: {e}")
            print("Server shutting down")
            exit()
        else:
            for addr, client in clients.items():
                try:
                    client.send(message.encode('utf-8'))
                    doc_ref = db.collection('server').document('clients')
                    doc_ref.update({
                        'clients': firestore.ArrayUnion([addr[0]])})
                except Exception as e:
                    print(f"Error sending message to client: {e}")
                    client.close()
                    remove(client)

            log_entry = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'log': f"Server: {message}"
            }

            document_id = log_entry['date']
            doc_ref = db.collection('logs').document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                existing_data = doc.to_dict()
                existing_logs = existing_data.get('logs', [])
                existing_logs.append(log_entry['log'])
                doc_ref.update({
                    'logs': existing_logs
                })
            else:
                doc_ref.set({
                    'date': log_entry['date'],
                    'logs': [log_entry['log']]
                })

# Remove client
def remove(connection):
    with clients_lock:
        addr = (connection.getpeername()[0], connection.getpeername()[1])
        if addr in clients:
            del clients[addr]
            db = firestore.client()
            doc_ref = db.collection('server').document('clients')
            doc_ref.update({
                'clients': firestore.ArrayRemove([addr[0]])})

def extract_target_ip(message):
    # Define the regex pattern to match the IP address at the start of the message
    pattern = r'^(\d+\.\d+\.\d+\.\d+)'
    match = re.search(pattern, message)
    if match:
        return match.group(1)
    return None


# Thread function for handling client connections
def threaded(c, addr):
    with clients_lock:
        clients[addr] = c
    while True:
        try:
            data = c.recv(1024)
            if not data:
                print(f'Bye {addr}')
                break
            message = data.decode('utf-8')
            print(f"Message from {addr}: {message}")

            # Extract target IP using regex
            target_ip = extract_target_ip(message)
            if target_ip:
                send_client(message, target_ip)
            else:
                print("No valid target IP found in the message")

            with clients_lock:
                print(f"Number of clients: {len(clients)}")
        except Exception as e:
            print(f"Error receiving data from {addr}: {e}")
            break
    remove(c)
    c.close()

# Send messages from the server
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

    start_new_thread(send_messages, ())

    while True:
        try:
            c, addr = s.accept()
            print('Connected to :', addr[0], ':', addr[1])
            start_new_thread(threaded, (c, addr))
        except Exception as e:
            print(f"Error accepting connections: {e}")
            break
    s.close()

if __name__ == '__main__':
    Main()
