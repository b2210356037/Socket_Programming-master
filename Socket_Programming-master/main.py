import sys
from PyQt5 import QtWidgets, QtCore
from ui_interface import Ui_MainWindow  # PyQt5 GUI dosyanızın adı


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupConnections()
        self.initializeDateTime()

        # Zamanlayıcı oluştur ve her 1000 ms (1 saniye) aralıklarla updateDateTime metodunu çağır
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # 1 saniyede bir

    def setupConnections(self):
        # Button'lara tıklama olaylarını bağlıyoruz
        self.ui.pushButton.clicked.connect(self.handlePushButtonClick)
        self.ui.pushButton_2.clicked.connect(self.handlePushButton2Click)

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

    def handlePushButtonClick(self):
        # Kullanıcıdan gelen mesajı al
        user_message = self.ui.lineEdit_2.text()

        # Mesajı textEdit widget'ına ekle
        self.ui.textEdit.append(user_message)

        # Düğmeye tıklanmasıyla bu fonksiyon çalışır
        QtWidgets.QMessageBox.information(self, "Button Clicked", "Your message is sent!")

    def handlePushButton2Click(self):
        # İkinci düğmeye tıklanmasıyla bu fonksiyon çalışır
        QtWidgets.QMessageBox.information(self, "Button Clicked", "Cancel Button Clicked!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
