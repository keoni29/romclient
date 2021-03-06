from fwlink import *
from fwpacket import *
from subprocess import Popen

def _print(message):
    print(message)


def _debugPrint(message):
  self.print('___debug__ ' + message)


def _nop():
  """ No operation. """
  pass

#///////////////////////////////////////////////////////////////////////////////
# Classes
#///////////////////////////////////////////////////////////////////////////////
class _State():
  """ Statemachine states enum """
  READY = 0
  DUMP_BEGIN = 1
  DUMP = 2
  DUMP_END = 3
  DUMP_ABORT = 4
  DUMP_FAIL = 5
  RESET = 6
  INIT = 7
  DUMP_TIMEOUT = 8

class BankSwitchMethod():
  """ Bankswitching types enum
  Special thanks to Kevin "Kevtris" Horton for these descriptions

  Attributes:
    NONE  No bankswitching.
    F6    FF6/FF7/FF8/FF9 bankswitching
    F8    FF8/FF9 bankswitching
    FA    FF8/FF9/FFA bankswitching (aka CBS' RAM Plus)
    E0    FE0-FF7 bankswitching (aka Parker Bros.)
    E7    FE0-FE7 bankswitching found on M-Network carts
    FE    01FE/11FE bankswitching (aka Activision Robot Tank)
    USER  User defined bankswitching
  """
  NONE = 0
  F6 = 1
  F8 = 2
  FA = 3
  E0 = 4
  E7 = 5
  FE = 6
  USER = 7

class _Rom():
  """ Storage class with random access """
  def __init__(self):
    pass


class RomClient():
  """ ROM dumping utility
  
  Attributes:
    _kTemporaryFilePath Path to temporary ROM dump file. After dumping a ROM this file is overwritten.
    _kMaxReadSize       Maximum no. of bytes to read from firmware at a time.
    _kDebugDataLength   Length of ROM dump. After receiving this many bytes, automatically stop reading.
  """

  _kTemporaryFilePath = '.tmp.a26'
  _kMaxReadSize = 9999
  _kDebugDataLength = 4096


  def __init__(self, 
                port = None, 
                log = _print, 
                debugLog = _debugPrint, 
                lockGui = _nop, 
                unlockGui = _nop):
    # Register callbacks
    self.log = log
    self.debugLog = debugLog
    self.unlockGui = unlockGui
    self.lockGui = lockGui

    # Reset lock
    self.unlockGui()

    # Set up firmware link
    self.setSerialReadTimeout(1)
    self.fw = Fw_Link()
    self.setSerialPort(port)
    self.setBankSwitchMethod(BankSwitchMethod.NONE)

    # Timeout ticks
    self.setTimeoutTicks(10)

    # Set up state machine
    self.dataValid = False
    self.state = _State.INIT
    
    # Auto launching emulator settings
    self.setLaunchEmulatorEnabled(False)
    self.setEmulatorPath('stella')

    # Set up ROM data
    self._clearRom()

#///////////////////////////////////////////////////////////////////////////////
# Public Methods
#///////////////////////////////////////////////////////////////////////////////
  def startDump(self):
    """
    Begin a ROM dump 
    :return: True if a ROM dump was started
    "rtype: bool
    """
    started = False
    if self.state == _State.READY:
      self.state = _State.DUMP_BEGIN
      self.debugLog('Begin dump')
      started = True
    else:
      self.debugLog('Busy')

    return started


  def dumpToFile(self, name):
    if self.startDump():
      self.log('Start ROM dump to file.')
      while not self.dataValid:
        abort = self.update()
        if abort:
          return
    else:
      self.log('Could not start ROM dump.')

    self.saveDump(name)
    if self.launchEmulatorEnabled:
      self.launchEmulator()
  
  def setLaunchEmulatorEnabled(self, state):
    self.launchEmulatorEnabled = state
    self.debugLog('launchEmulatorEnabled = ' + str(self.launchEmulatorEnabled))
  
  def setEmulatorPath(self, path):
    self.emulatorPath = path

  def launchEmulator(self):
    cmd = self.emulatorPath
    args = self.getLastFileName()
    if cmd and args:
      self.emulatorProcess = Popen([cmd, args])
      self.log('Started emulator')
  
  def terminateEmulator(self):
    if self.emulatorProcess:
      self.emulatorProcess.terminate()


  def setBankSwitchMethod(self, method = None):
    self.bankSwitchMethod = method
  
  def setSerialReadTimeout(self, timeout):
    self.serialReadTimeOut = timeout

  def setSerialPort(self, port):
    retv = False

    if port:
      if self.fw.open(port, self.serialReadTimeOut):
        self.log('Opened serial port ' + port)
        retv = True
      else:
        self.log('Could not open serial port ' + port)

    return retv

  def setTimeoutTicks(self, ticks):
    self.timeoutTicks = ticks

  def update(self):
    """
    Main loop and state machine of the rom reader. Can be used as timer callback or in a loop.

    :return: True if operation was aborted
    :rtype: bool
    """
    abort = False

    ### Initialize the state machine
    if self.state == _State.INIT:
      self.state = _State.READY
      pass
      
    ### Ready to begin a ROM dump
    if self.state == _State.READY:           
      pass


    ### Begin a ROM dump
    if self.state == _State.DUMP_BEGIN:
      self.log('Starting ROM dump')
      self.state = _State.DUMP
      self.lockGui()
      self.timeoutCount = self.timeoutTicks

      self.dataLength = 0
      self._clearRom()

      # Synchronize with firmware (just in case)
      self.fw.sync()

    ### Dumping the ROM
    if self.state == _State.DUMP: #TODO redo state machine preferably with bankswitching address generator support
      if self.timeoutCount:
        self.timeoutCount -= 1
        length = 256#TODO avoid magic numbers
        request = Fw_Packet(Fw_Command.READ_BLOCK, address=0x1000, length=length)

        for i in range(0,16): #TODO avoid magic numbers
          reply = self.fw.transceive(request)
          self.romData.extend(reply.getData())
          self.dataLength += length
          request.addressNextBlock()
        
        self.state = _State.DUMP_END
      else:
        self.state = _State.DUMP_TIMEOUT

    ### Dumped the ROM succesfully
    if self.state == _State.DUMP_END:
      self.log('Done! Rom has been dumped succesfully.')
      self.dataValid = True

      # Always make a temporary dump
      self.saveDump(self._kTemporaryFilePath)

      if self.launchEmulatorEnabled:
        self.launchEmulator()

      self.state = _State.RESET

    if self.state == _State.DUMP_TIMEOUT:
      self.log('Operation timed out.')
      if self.dataLength == 0:
        self.debugLog('Total bytes received ' + str(self.dataLength))
      self.state = _State.DUMP_FAIL

    ### ROM dump was aborted
    if self.state == _State.DUMP_ABORT:
      self.log('Dump operation aborted.')
      self.state = _State.DUMP_FAIL

    ### ROM dump has failed
    if self.state == _State.DUMP_FAIL:
      self.log('ROM dump failed.')
      self.unlockGui()
      abort = True
      self.state = _State.RESET

    ### Reset state machine
    if self.state == _State.RESET:
      self.unlockGui()
      self.state = _State.READY


  def getLastFileName(self):
    return self.lastRomFileName

  def saveDump(self, name):
    """
    Save ROM dump to a file 
    :param name: Name/path to file.
    :type name: str
    """
    if self.dataValid:
      self.log('Saving ROM to file.')
      try:
        with open(name, 'wb+') as f:
          f.write(self.romData)
        self.lastRomFileName = name

      except IOError as e:
        self.log('Could not write to file.')
        self.debugLog('IOError: (' + e.errno + '): '  + e.strerror)

#///////////////////////////////////////////////////////////////////////////////
# Private Methods
#///////////////////////////////////////////////////////////////////////////////
  def _clearRom(self):
    self.romData = bytearray()


if __name__ == '__main__':
  # TODO implement
  pass