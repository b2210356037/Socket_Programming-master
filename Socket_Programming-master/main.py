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

load_dotenv()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupConnections()
        self.initializeDateTime()

        # Takvim widget'ını İngilizce olarak ayarla
        self.ui.calendarWidget.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
    
        # TCP bağlantısını başlat
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.77.10', 12345))

        self.host_ip = self.client_socket.getsockname()[0]

        # Mesajları almak için bir thread başlat
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Timer oluştur ve updateDateTime metodunu her 1000 ms (1 saniye) çağır
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # Her 1 saniye

        # Google Generative AI modelini yapılandır
        self.configureGenerativeAI()

    def setupConnections(self):
        # Buton tıklamalarını ilgili işleyicilere bağla
        self.ui.pushButton.clicked.connect(self.handlePushButtonClick)
        # Takvim widget'ının tıklama sinyalini show_date metoduna bağla
        self.ui.calendarWidget.clicked.connect(self.show_date)
        # AI ile içerik üretme butonunu bağla
        self.ui.pushButton_2.clicked.connect(self.handlePushButton2Click)

    def initializeDateTime(self):
        # Şu anki tarih ve saati al ve widget'lara ayarla
        current_time = QtCore.QTime.currentTime()
        current_date = QtCore.QDate.currentDate()

        # Tarih ve saati widget'lara ayarla
        self.ui.timeEdit.setTime(current_time)
        self.ui.dateEdit.setDate(current_date)

    def updateDateTime(self):
        # Şu anki tarih ve saati al ve widget'lara ayarla
        current_time = QtCore.QTime.currentTime()
        current_date = QtCore.QDate.currentDate()

        # Tarih ve saati widget'lara ayarla
        self.ui.timeEdit.setTime(current_time)
        self.ui.dateEdit.setDate(current_date)

    def show_date(self, date):
        # Tarihi İngilizce formatta mesaj kutusunda göster
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        formatted_date = locale.toString(date, QLocale.LongFormat)
        QtWidgets.QMessageBox.information(self, "Seçilen Tarih", formatted_date)

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
        # AI ile sohbet etme
        user_prompt = self.ui.lineEdit_2.text()  # Kullanıcının AI'ye göndermek istediği mesajı al
        if user_prompt:
            try:
                response = self.model.generate_content(user_prompt)
                # AI'dan gelen yanıtı textEdit widget'ına yazdır
                self.ui.textEdit.append(f"AI Yanıtı: {response.text}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "AI Hatası", f"AI yanıtı alınamadı: {e}")
            # lineEdit widget'ını temizle
            self.ui.lineEdit_2.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Boş Mesaj", "AI'ye gönderilecek bir mesaj girin.")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    # Mesajı textEdit widget'ına ekle
                    # Gönderen sunucu IP'si ise mesajı kırmızı olarak göster
                    if self.host_ip == self.client_socket.getsockname()[0]:
                        self.ui.textEdit.append(f"<font color='red'> Sunucu: {message}</font>")
                    else:
                        self.ui.textEdit.append(message)
                else:
                    break
            except:
                break

    def configureGenerativeAI(self):
        # API anahtarını ortam değişkenlerinden yapılandır
        api_key = os.getenv("GOOGLE_APIKEY")
        if api_key:
            genai.configure(api_key=os.environ["GOOGLE_APIKEY"])
            # Belirtilen model ID'si ile bir GenerativeModel örneği oluştur
            self.model = genai.GenerativeModel('gemini-1.0-pro-latest')
        else:
            QtWidgets.QMessageBox.critical(self, "API Anahtar Hatası", "GOOGLE_API_KEY ortam değişkeni tanımlı değil.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
