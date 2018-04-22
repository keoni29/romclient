""" GUI wrapper for ROM dumping utility """

import sys
from emulator import *
from gui import *
from romclient import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog


class RomClientGui:
  kSerialTimeoutS = 3 # seconds

  def __init__(self):
      # Set up GUI
    self.app = QtWidgets.QApplication(sys.argv)
    self.MainWindow = QtWidgets.QMainWindow()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self.MainWindow)
    self.ui.actionSave.triggered.connect(self.handleFileSave)
    self.ui.actionExit.triggered.connect(self.handleFileExit)
    self.ui.buttonScan.pressed.connect(self.handleSerialPortScan)
    self.ui.comboBoxSerial.activated.connect(self.handleSerialPortSelect)
    self.ui.actionDebug.toggled.connect(self.handleDebugOption)
    self.ui.actionAuto_Launch.toggled.connect(self.handleAutoLaunch)
    self.ui.actionLaunch_Now.triggered.connect(self.handleLaunchNow)
    #self.autoLaunch = False

    # Set up romclient
    self.rc = RomClient(None, self.rcLog, self.rcDebugLog, self.lockGui, self.unlockGui)
    self.handleSerialPortScan()
    self.handleSerialPortSelect(0)

    self.ui.buttonDump.pressed.connect(self.handleDump)

    self.handleDebugOption(False)


  def start(self):
      # Start GUI application
    self.MainWindow.show()
    sys.exit(self.app.exec_())


  def handleDump(self):
    self.rc.dumpRom()

    if self.autoLaunch:
      self.handleLaunchNow()

  def handleAutoLaunch(self, checked):
    self.autoLaunch = checked


  def handleLaunchNow(self):
    tmp = '.tmp.a26'
    self.rc.saveDump(tmp)
    Emulator().launch(tmp)


  def fileSaveDialog(self):  
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ =  QFileDialog.getSaveFileName(self.MainWindow, 'Save File',
              '',
              'ROM Images (*.a26 *.bin *.rom)')
    return fileName


  def handleFileSave(self):
    fileName = self.fileSaveDialog()
    if fileName:
      self.debugLog('Saving to file')
      self.debugLog(fileName)
      self.rc.saveDump(fileName)
      # TODO save buffer to file
    else:
      pass


  def log(self, message):
    self.ui.messageLog.append(message)


  def debugLog(self, message):
    if self.debugLogEnabled:
      self.log('debug____ :' + message)


  def rcLog(self, message):
    self.log('romclient : ' + message)


  def rcDebugLog(self, message):
    self.debugLog('romclient : ' + message)


  def logClear(self):
    self.ui.messageLog.setText('')


  def handleFileExit(self):
    exit()


  def handleDebugOption(self, checked):
    if checked:
      self.debugLogEnabled = True
    else:
      self.debugLogEnabled = False


  def handleSerialPortScan(self):
    ports = self.rc.scanSerial()    
    self.ui.comboBoxSerial.clear()
    if ports:
      for port in ports:
        self.ui.comboBoxSerial.addItem(port.device, port.device)
    else:
      self.ui.comboBoxSerial.addItem('None')


  def handleSerialPortSelect(self, item):
    port = self.ui.comboBoxSerial.itemData(item)
    self.rc.setSerialPort(port, self.kSerialTimeoutS)


  def lockGui(self):
    self.lock(True)


  def unlockGui(self):
    self.lock(False)


  def lock(self, locked):
    enabled = not locked
    self.ui.menubar.setEnabled(enabled)
    self.ui.buttonDump.setEnabled(enabled)
    self.ui.groupBox.setEnabled(enabled)


if __name__ == "__main__":
  app = RomClientGui()
  app.start()
