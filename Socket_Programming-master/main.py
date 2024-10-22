import sys
import socket
import threading
import google.generativeai as genai
import os
from google.cloud import firestore

import sys
import socket
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QLocale
from interface_ui import Ui_MainWindow  # Your PyQt5 GUI file name
from firebaseInitialize import *
from dotenv import load_dotenv
from firebase_admin import firestore 
from datetime import datetime
from TCPServer import clients
from PyQt5.QtCore import pyqtSignal


load_dotenv()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Connect the combobox click event to the on_combobox_click method
        db = firestore.client()
        self.setupConnections(db)
        self.initializeDateTime()
        # Initialize selected_client_ip
        self.selected_client_ip = None

        # Set the calendar widget to English
        self.ui.calendarWidget.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
    
        # Start TCP connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.77.10', 12345))

        self.host_ip = self.client_socket.getsockname()[0]

        # Start a thread to receive messages
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Create a timer and call updateDateTime method every 1000 ms (1 second)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # Every 1 second

        # Configure the Google Generative AI model
        self.configureGenerativeAI()
        #sself.ui.comboBox.activated.connect(self.add_items_combobox)


        self.ui.comboBox.currentIndexChanged.connect(self.on_combobox_change)
        self.add_items_combobox(db, self.ui.comboBox)
    
    def setupConnections(self, db):
        # Connect button clicks to their respective handlers
        self.ui.pushButton.clicked.connect(self.sendMessageToServer)
        # Connect the calendar widget's clicked signal to show_date method
        self.ui.calendarWidget.clicked.connect(self.show_date)
        # Connect button for generating content with AI
        self.ui.pushButton_2.clicked.connect(self.sendMessageToAI)
        # Connect the refresh button to add_items_combobox method
        self.ui.pushButton_4.clicked.connect(self.refresh_clients)

    def refresh_clients(self):
        # Refresh the clients in the combobox via Firestore
        self.ui.comboBox.clear()
        db = firestore.client()
        doc_ref = db.collection('server').document('clients')

        try:
            doc = doc_ref.get()
            if doc.exists:
                clients_data = doc.to_dict().get('clients', [])
                self.ui.comboBox.addItems(clients_data)
            else:
                print("No clients found")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error fetching clients: {e}")

    def initializeDateTime(self):
        # Get the current date and time and set them to the widgets
        current_time = QtCore.QTime.currentTime()
        current_date = QtCore.QDate.currentDate()

        # Set date and time to widgets
        self.ui.timeEdit.setTime(current_time)
        self.ui.dateEdit.setDate(current_date)

    def updateDateTime(self):
        # Get the current date and time and set them to the widgets
        current_time = QtCore.QTime.currentTime()
        current_date = QtCore.QDate.currentDate()

        # Set date and time to widgets
        self.ui.timeEdit.setTime(current_time)
        self.ui.dateEdit.setDate(current_date)

    def show_date(self, date):
        # Display the total log entries for the selected date
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        formatted_date = locale.toString(date, QLocale.LongFormat)

        try:
            # Get the document ID
            document_id = date.toString("yyyy-MM-dd")
            
            # Reference to the document
            doc_ref = db.collection('logs').document(document_id)

            for log in doc_ref.get().to_dict().get('logs', []):
                self.ui.textEdit.append(log)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error fetching logs: {e}")

        QtWidgets.QMessageBox.information(self, "Selected Date", formatted_date)

    def on_combobox_change(self):
        # Seçilen IP adresini alın
        self.selected_client_ip = self.ui.comboBox.currentText()
        #print("SELECTED: "+ self.selected_client_ip)

    def sendMessageToServer(self):
        if self.selected_client_ip is None:
            QtWidgets.QMessageBox.warning(self, "No Client Selected", "Please select a client.")
            return

        # Get the message from the user
        user_message = self.ui.lineEdit_2.text()

        # If no message is entered, show a warning
        if not user_message:
            QtWidgets.QMessageBox.warning(self, "Empty Message", "Please enter a message.")
            return

        # Send the message to the selected client via the TCP server
        message = f"{self.selected_client_ip}: {user_message}"

        if self.selected_client_ip == "Server":
            self.ui.textEdit.append(f"{self.host_ip}: {user_message}")
        else:
            try:
                self.ui.textEdit.append(f"To {self.selected_client_ip}: {user_message}")
                self.client_socket.sendall(message.encode())
                print("Message sent to client: " + self.selected_client_ip)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send message: {e}")
                
        # Clear the lineEdit widget
        self.ui.lineEdit_2.clear()


        # Prepare the log entry
        log_entry = {
            'date': QtCore.QDate.currentDate().toString("yyyy-MM-dd"),
            'log': f"{self.host_ip}: {user_message}"
        }

        # Get the current date as the document ID
        document_id = QtCore.QDate.currentDate().toString("yyyy-MM-dd")

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

        # Get the current date as the document ID
        document_id = QtCore.QDate.currentDate().toString("yyyy-MM-dd")

        # Reference to the document
        doc_ref = db.collection('logs').document(document_id)

        # Clear the lineEdit widget
        self.ui.lineEdit_2.clear()

    def sendMessageToAI(self):
        # Chat with AI
        user_prompt = self.ui.lineEdit_2.text()  # Get the message to send to AI from the user
        if user_prompt:
            try:
                response = self.model.generate_content(user_prompt)
                # Add the AI response to the textEdit widget
                self.ui.textEdit.append(f"AI Response: {response.text}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "AI Error", f"AI response not received: {e}")
            # Clear the lineEdit widget
            self.ui.lineEdit_2.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Empty Message", "Enter a message to send to AI.")

    def receive_messages(self):
        while True:
            try:
                message, addr = self.client_socket.recvfrom(1024)
                sender_ip = self.client_socket.getpeername()[0]
                if message:
                    # Add the message to the textEdit widget
                    # if sender_ip == self.host_ip:
                        # self.ui.textEdit.append(f"<font color='red'> 'Server': {message}</font>")
                    # else:
                        self.ui.textEdit.append(f"<font color='blue'> {sender_ip}: {message}</font>")
                else:
                    break
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error receiving message: {e}")
                break


    def configureGenerativeAI(self):
        # Configure the API key from environment variables
        api_key = os.getenv("GOOGLE_APIKEY")
        if api_key:
            genai.configure(api_key=os.environ["GOOGLE_APIKEY"])
            # Create a GenerativeModel instance with the specified model ID
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            QtWidgets.QMessageBox.critical(self, "API Key Error", "GOOGLE_API_KEY environment variable is not set.")
    
    def add_items_combobox(self, db, comboBox):
        try:
            clients = db.collection('server').document('clients').get().to_dict().get('clients', [])
            comboBox.clear()  # Clear existing items
            for client in clients:
                comboBox.addItem(client)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error fetching clients: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())