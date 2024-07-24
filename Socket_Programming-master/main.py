import sys
import socket
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QLocale
from interface_ui import Ui_MainWindow  # Your PyQt5 GUI file name
from firebaseInitialize import *
from dotenv import load_dotenv
from firebase_admin import firestore 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupConnections()
        self.initializeDateTime()

        # Set the calendar widget to English
        self.ui.calendarWidget.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
    
        # Start TCP connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.77.10', 12345))

        self.host_ip = self.client_socket.getsockname()[0]
        host_ip = "192.168.77.10"
        # Start a thread to receive messages
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Create a timer and call updateDateTime method every 1000 ms (1 second)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # Every 1 second

    def setupConnections(self):
        # Connect button clicks to their respective handlers
        self.ui.pushButton.clicked.connect(self.handlePushButtonClick)
        # Connect the calendar widget's clicked signal to show_date method
        self.ui.calendarWidget.clicked.connect(self.show_date)
        

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
        # Display the date in English format in a message box
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        formatted_date = locale.toString(date, QLocale.LongFormat)
        QtWidgets.QMessageBox.information(self, "Selected Date", formatted_date)
        #initialize firebase database

    def handlePushButtonClick(self):
        # Get the message from the user
        user_message = self.ui.lineEdit_2.text()

        # Add the message to the textEdit widget
        self.ui.textEdit.append(f"{self.host_ip}: {user_message}")

        # Send the message to the TCP server
        self.client_socket.sendall(f"{self.host_ip}: {user_message}".encode())

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

        # Clear the lineEdit widget
        self.ui.lineEdit_2.clear()



    def handlePushButton2Click(self):
        # This function is called when the second button is clicked
        QtWidgets.QMessageBox.information(self, "Button Clicked", "Cancel Button Clicked!")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    # Add the message to the textEdit widget
                    # If the sender has the server IP, display the message in red
                    if(self.host_ip == self.client_socket.getsockname()[0]):
                        self.ui.textEdit.append(f"<font color='red'> Server: {message}</font>")
                    else:
                        self.ui.textEdit.append(message)
                else:
                    break
            except:
                break

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
