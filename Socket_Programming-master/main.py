import sys
import socket
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QLocale
from interface_ui import Ui_MainWindow  # PyQt5 GUI dosyanızın adı


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupConnections()
        self.initializeDateTime()


        # Takvim widget'ını İngilizceye ayarlama
        self.ui.calendarWidget.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
    

        # Tcp bağlantısı başlatma
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.77.10', 12345))

        self.host_ip = self.client_socket.getsockname()[0]
        host_ip = "192.168.77.10"
        # Mesajları almak için iş parçacığını başlat
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Zamanlayıcı oluştur ve her 1000 ms (1 saniye) aralıklarla updateDateTime metodunu çağır
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # 1 saniyede bir

    def setupConnections(self):
        # Button'lara tıklama olaylarını bağlıyoruz
        self.ui.pushButton.clicked.connect(self.handlePushButtonClick)
        # Calendar widget'ın tıklama sinyalini show_date metoduna bağlıyoruz
        self.ui.calendarWidget.clicked.connect(self.show_date)
        

    def initializeDateTime(self):
        # Mevcut tarihi ve saati al ve widget'lara ata
        current_time = QtCore.QTime.currentTime()
        current_date = QtCore.QDate.currentDate()

        # Widget'lara tarih ve saat atama
        self.ui.timeEdit.setTime(current_time)
        self.ui.dateEdit.setDate(current_date)

    def updateDateTime(self):
        # Mevcut tarihi ve saati al ve widget'lara ata
        current_time = QtCore.QTime.currentTime()
        current_date = QtCore.QDate.currentDate()

        # Widget'lara tarih ve saat atama
        self.ui.timeEdit.setTime(current_time)
        self.ui.dateEdit.setDate(current_date)

    def show_date(self, date):
    # Tarihi QDate tipinde alıp bir mesaj kutusunda gösterme
     QtWidgets.QMessageBox.information(self, "Selected Date", date.toString())


    def handlePushButtonClick(self):
        # Kullanıcıdan gelen mesajı al
        user_message = self.ui.lineEdit_2.text()

        # Mesajı textEdit widget'ına ekle
        self.ui.textEdit.append(f"{self.host_ip}: {user_message}")

        # Mesajı TCP sunucusuna gönder
        self.client_socket.sendall(f"{self.host_ip}: {user_message}".encode())

        # LineEdit widget'ını temizle
        self.ui.lineEdit_2.clear()

    def handlePushButton2Click(self):
        # İkinci düğmeye tıklanmasıyla bu fonksiyon çalışır
        QtWidgets.QMessageBox.information(self, "Button Clicked", "Cancel Button Clicked!")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    # Mesajı textEdit widget'ına ekle
                    #if the sender has the server ip, display the message in red
                    if(self.host_ip == self.client_socket.getsockname()[0]):
                        self.ui.textEdit.append(f"<font color='red'> Server: {message}</font>")


                    # if message.startswith("Server:"):
                    #     self.ui.textEdit.append(f"<font color='red'>{message}</font>")
                    else:
                        self.ui.textEdit.append(message)
                    #self.ui.textEdit.append(message)
                else:
                    break
            except:
                break
    
          
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
