from rom import *

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

class RomDump():

  def __init__(self):
    # Timeout ticks
    self.setTimeoutTicks(10)

    # Set up state machine
    self.state = _State.INIT


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

      # Test: 'R' character initiates rom dump sequence
      success,errorstr = self.fw.write(b'R')
      if not success:
        self.debugLog('Write failed. Reason:' + errorstr)
        self.state = _State.DUMP_FAIL

    ### Dumping the ROM
    if self.state == _State.DUMP:
      if self.timeoutCount:
        self.timeoutCount -= 1
        self.dump()
        #self.debugLog(str(self.timeoutCount))
      else:
        self.state = _State.DUMP_TIMEOUT

    ### Dumped the ROM succesfully
    if self.state == _State.DUMP_END:
      self.dumpEnd()
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