""" GUI wrapper for ROM dumping utility """

import serial.tools.list_ports
import sys
from gui import *
from romclient import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer

# Timeout time (in ms) is:
#   kUpdateTimerInterval * kReadTimeoutTicks
kUpdateTimerInterval = 1000 # ms
kSerialTimeoutS = 3 # s
kReadTimeoutTicks = 5
debugLogEnabled = False

#//////////////////////////////////////////////////////////////////////////////
# Emulator
#//////////////////////////////////////////////////////////////////////////////
def handleAutoLaunch(checked):
  rc.setLaunchEmulatorEnabled(checked)
    

#//////////////////////////////////////////////////////////////////////////////
# File saving
#//////////////////////////////////////////////////////////////////////////////
def fileSaveDialog():  
  options = QFileDialog.Options()
  options |= QFileDialog.DontUseNativeDialog
  fileName, _ =  QFileDialog.getSaveFileName(MainWindow, 'Save File',
            '',
            'ROM Images (*.a26 *.bin *.rom)')
  return fileName


def fileSave():
  fileName = fileSaveDialog()
  if fileName:
    debugLog('Saving to file')
    debugLog(fileName)
    rc.saveDump(fileName)
    # TODO save buffer to file
  else:
    pass

#//////////////////////////////////////////////////////////////////////////////
# Log messages
#//////////////////////////////////////////////////////////////////////////////
def log(message):
  ui.messageLog.append(message)


def debugLog(message):
  if debugLogEnabled:
    log('debug____ :' + message)


def rcLog(message):
  log('romclient : ' + message)


def rcDebugLog(message):
  debugLog('romclient : ' + message)


def logClear():
  ui.messageLog.setText('')


def fileExit():
  exit()


def handleDebugOption(checked):
  global debugLogEnabled
  if checked:
    debugLogEnabled = True
    debugLog('Enabled debug logs')
  else:
    debugLog('Disabled debug logs')
    debugLogEnabled = False

#//////////////////////////////////////////////////////////////////////////////
# Serial port selection
#//////////////////////////////////////////////////////////////////////////////
def serialPortScan():
  ports = serial.tools.list_ports.comports()
  
  ui.comboBoxSerial.clear()
  if ports:
    for port in ports:
      ui.comboBoxSerial.addItem(port.device, port.device)
  else:
    ui.comboBoxSerial.addItem('None')


def serialPortSelect(item):
  port = ui.comboBoxSerial.itemData(item)
  rc.setSerialPort(port)

def update():
  rc.update()
  debugLog('tick')

#//////////////////////////////////////////////////////////////////////////////
# GUI Lock
#//////////////////////////////////////////////////////////////////////////////

def lockGui():
  debugLog('LockParameters')
  lock(True)

def unlockGui():
  debugLog('UnlockParameters')
  lock(False)

def lock(locked):
  enabled = not locked
  ui.menubar.setEnabled(enabled)
  ui.buttonDump.setEnabled(enabled)
  ui.groupBox.setEnabled(enabled)

#//////////////////////////////////////////////////////////////////////////////
# Main
#//////////////////////////////////////////////////////////////////////////////
if __name__ == "__main__":
  # Set up GUI
  app = QtWidgets.QApplication(sys.argv)
  MainWindow = QtWidgets.QMainWindow()
  ui = Ui_MainWindow()
  ui.setupUi(MainWindow)
  ui.actionSave.triggered.connect(fileSave)
  ui.actionExit.triggered.connect(fileExit)
  ui.buttonScan.pressed.connect(serialPortScan)
  ui.comboBoxSerial.activated.connect(serialPortSelect)
  ui.actionDebug.toggled.connect(handleDebugOption)
  ui.actionAuto_Launch.toggled.connect(handleAutoLaunch)

  # Set up romclient
  rc = RomClient(None, rcLog, rcDebugLog, lockGui, unlockGui)
  serialPortScan()
  serialPortSelect(0)
  rc.setSerialReadTimeout(kSerialTimeoutS)
  rc.setTimeoutTicks(kReadTimeoutTicks)

  ui.buttonDump.pressed.connect(rc.startDump)
  #TODO add stop dump button

  updateTimer = QTimer()
  updateTimer.timeout.connect(update)
  updateTimer.start(kUpdateTimerInterval)

  # Start GUI application
  MainWindow.show()
  sys.exit(app.exec_())
