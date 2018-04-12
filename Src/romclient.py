from romdump import *
import emulator

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

class RomClient():
  """ ROM dumping utility
  
  Attributes:
    _kTemporaryFilePath Path to temporary ROM dump file. After dumping a ROM this file is overwritten.
  """

  _kTemporaryFilePath = '.tmp.a26'

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
    self.update = _nop

    # Reset lock
    self.unlockGui()
    
    # Auto launching emulator settings
    self.setLaunchEmulatorEnabled(False)

    # Set up ROM
    self.rom = Rom()

#///////////////////////////////////////////////////////////////////////////////
# Public Methods
#///////////////////////////////////////////////////////////////////////////////
  def dumpToFile(self, name):
    #TODO implement
    pass
  
  def dumpStart(self):
    #TODO implement
    pass

  def dump(self):
    self.rom.dump()

  def dumpEnd(self):
    self.log('Done! Rom has been dumped succesfully.')

    # Always make a temporary dump
    self.saveDump(self._kTemporaryFilePath)

    if self.launchEmulatorEnabled:
      Emulator.launch()


  def saveDump(self, name):
    """
    Save ROM dump to a file 
    :param name: Name/path to file.
    :type name: str
    """
    if self.rom.dumped():
      self.log('Saving ROM to file.')
      try:
        with open(name, 'wb+') as f:
          f.write(self.romData)
        self.lastRomFileName = name

      except IOError as e:
        self.log('Could not write to file.')
        self.debugLog('IOError: (' + e.errno + '): '  + e.strerror)

  def getLastFileName(self):
    return self.lastRomFileName


  def setLaunchEmulatorEnabled(self, state):
    self.launchEmulatorEnabled = state
    self.debugLog('launchEmulatorEnabled = ' + str(self.launchEmulatorEnabled))
  

  def setSerialReadTimeout(self, timeout):
    self.rom.setSerialReadTimeout(timeout)


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


if __name__ == '__main__':
  # TODO implement
  pass