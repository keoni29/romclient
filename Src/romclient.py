""" VCS game ROM dumping utility """

def log(message):
    ui.messageLog.append(message)

def startRead():
    log('Starting ROM Dump')

if __name__ == "__main__":
    import serial
    import sys
    from gui import *
    from PyQt5 import QtCore, QtGui, QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.pushButtonGo.pressed.connect(startRead)
    MainWindow.show()
    sys.exit(app.exec_())
