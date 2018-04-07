from fwlink import *

class State():
  READY = 0
  DUMP_BEGIN = 1
  DUMP = 2
  DUMP_END = 3
  DUMP_ABORT = 4
  DUMP_FAIL = 5
  RESET = 6
  INIT = 7

class RomClient():
  """ ROM dumping utility """
  def __init__( self, 
                port = None, 
                log = None, 
                debugLog = None, 
                lockGui = None, 
                unlockGui = None):
    # Register callbacks
    if log:
      self.log = log
    else:
      self.log = self.print
    
    if debugLog:
      self.debugLog = debugLog
    else:
      self.debugLog = self.debugPrint

    self.unlockGui = unlockGui
    self.lockGui = lockGui

    # Reset parameter lock
    self.resetLock()

    # Set up firmware link
    self.fw = Fw_Link()
    self.setSerialPort(port)
    self.setBankSwitchMethod(None)

    # Set up state machine
    self.dataValid = False
    self.state = State.INIT
    

    # Set up ROM data
    self.clearRom()

  def clearRom(self):
    self.romData = bytearray()

  def lock(self):
    self.parameterLock = True
    if self.lockGui:
      self.lockGui()


  def unlock(self):
    self.parameterLock = False
    if self.unlockGui:
      self.unlockGui()

  def resetLock(self):
    self.parameterLock = False
    if self.unlockGui:
      self.unlockGui()

  def locked(self):
    return self.parameterLock

  def setBankSwitchMethod(self, method = None):
    if not self.locked():
      self.bankSwitchMethod = method
  

  def setSerialPort(self, port):
    retv = False

    if not self.locked():
      if port:
        if self.fw.open(port):
          self.log('Opened serial port ' + port)
          retv = True
        else:
          self.log('Could not open serial port ' + port)

    return retv


  def startDump(self):
    if self.state == State.READY:
      self.state = State.DUMP_BEGIN
      self.debugLog('Begin dump')
    else:
      self.debugLog('Busy')


  def update(self):
    if self.state == State.INIT:
      self.state = State.READY
      pass
      
    elif self.state == State.READY:           
      pass

    elif self.state == State.DUMP_BEGIN:
      self.log('Starting ROM dump')
      self.state = State.DUMP
      self.lock()
      self.debugCount = 50

      self.clearRom()

      # Test: 'R' character initiates rom dump sequence
      self.fw.write(b'R')

    elif self.state == State.DUMP:
      if self.debugCount:
        self.debugCount -= 1
        self.debugLog(str(self.debugCount))

        success,data = self.fw.read(500)
        if not success:
          self.state = State.DUMP_FAIL
        elif len(data):
          self.romData.extend(data)
          self.debugLog('Receive' + str(len(data)) + 'bytes')
          # try:
          #   self.log('UTF-8: ' + data.decode('utf-8'))
          # except:
          #   self.log('HEX: ' + ''.join('{:02x}'.format(x, x) for x in data))
      else:
        self.state = State.DUMP_END

    elif self.state == State.DUMP_END:
      self.log('Done! Rom has been dumped succesfully.')
      self.dataValid = True
      self.state = State.RESET

    elif self.state == State.DUMP_ABORT:
      self.log('ROM dump aborted.')
      self.state = State.RESET

    elif self.state == State.DUMP_FAIL:
      self.log('ROM dump failed.')
      self.state = State.RESET

    elif self.state == State.RESET:
      self.unlock()
      self.state = State.READY

  def saveDump(self, name):
    if not self.locked() and self.dataValid:
      self.log('Saving data')
      with open(name, 'wb+') as f:
        try:
          f.write(self.romData)
        except IOError as e:
          print("IOError: (", e.errno, "):", e.strerror)


  def print(self, message):
    print(message)


  def debugPrint(self, message):
    self.print('[DEBUG]' + message)


if __name__ == '__main__':
  # TODO implement
  pass