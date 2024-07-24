import sys
import socket
import threading
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QLocale
from interface_ui import Ui_MainWindow  # Your PyQt5 GUI file name

load_dotenv()

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

    def setupConnections(self):
        # Connect button clicks to their respective handlers
        self.ui.pushButton.clicked.connect(self.handlePushButtonClick)
        # Connect the calendar widget's clicked signal to show_date method
        self.ui.calendarWidget.clicked.connect(self.show_date)
        # Connect button for generating content with AI
        self.ui.pushButton_2.clicked.connect(self.handlePushButton2Click)

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

    def handlePushButtonClick(self):
        # Get the message from the user
        user_message = self.ui.lineEdit_2.text()

        # Add the message to the textEdit widget
        self.ui.textEdit.append(f"{self.host_ip}: {user_message}")

        # Send the message to the TCP server
        self.client_socket.sendall(f"{self.host_ip}: {user_message}".encode())

        # Clear the lineEdit widget
        self.ui.lineEdit_2.clear()

    def handlePushButton2Click(self):
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
                message = self.client_socket.recv(1024).decode()
                if message:
                    # Add the message to the textEdit widget
                    # If the sender has the server IP, display the message in red
                    if self.host_ip == self.client_socket.getsockname()[0]:
                        self.ui.textEdit.append(f"<font color='red'> Server: {message}</font>")
                    else:
                        self.ui.textEdit.append(message)
                else:
                    break
            except:
                break

    def configureGenerativeAI(self):
        # Configure the API key from environment variables
        api_key = os.getenv("GOOGLE_APIKEY")
        if api_key:
            genai.configure(api_key=os.environ["GOOGLE_APIKEY"])
            # Create a GenerativeModel instance with the specified model ID
            self.model = genai.GenerativeModel('gemini-1.0-pro-latest')
        else:
            QtWidgets.QMessageBox.critical(self, "API Key Error", "GOOGLE_API_KEY environment variable is not set.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
