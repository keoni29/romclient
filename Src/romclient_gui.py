""" GUI wrapper for ROM dumping utility """
import sys
from gui import *
import romclient as rc
import fwlink
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
    self.handleDebugOption(self.ui.actionDebug.isChecked())
    self.ui.actionAuto_Launch.toggled.connect(self.handleAutoLaunch)
    self.ui.actionLaunch_Now.triggered.connect(self.handleLaunchNow)
    self.handleAutoLaunch(self.ui.actionAuto_Launch.isChecked())
    self.ui.buttonDump.pressed.connect(self.handleDump)

    # Set up serial port
    self.fw = fwlink.Fw_Link()
    self.handleSerialPortScan()
    self.handleSerialPortSelect(0)

    self.rom = None


  def start(self):
      # Start GUI application
    self.MainWindow.show()
    sys.exit(self.app.exec_())


  def handleDump(self):
    self.rom = rc.dumpRom(self.fw)

    if self.autoLaunch:
      self.handleLaunchNow()

  def handleAutoLaunch(self, checked):
    self.autoLaunch = checked


  def handleLaunchNow(self):
    if self.rom:
      tmp = '.tmp.a26'
      saved = rc.saveDump(tmp, self.rom)
      if not saved:
        self.log('Could not save file')
      rc.launch(rc.kEmulatorPath, tmp)


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
      saved = rc.saveDump(fileName, self.rom)
      if not saved:
        self.log('Could not save file')
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
    ports = self.fw.scan()
    self.ui.comboBoxSerial.clear()
    if ports:
      for port in ports:
        self.ui.comboBoxSerial.addItem(port.device, port.device)
    else:
      self.ui.comboBoxSerial.addItem('None')


  def handleSerialPortSelect(self, item):
    port = self.ui.comboBoxSerial.itemData(item)
    self.fw.open(port, self.kSerialTimeoutS)


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
