from fwpacket import *
from fwlink import *
import rom as ROM
import argparse


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


class RomClient():
  """ ROM dumping utility """

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

    self.rom = ROM.Rom()
    self.fw = Fw_Link()

    self.bankSwitchMethod = BankSwitchMethod.NONE

    self.autoLaunch = False

#///////////////////////////////////////////////////////////////////////////////
# Public Methods
#///////////////////////////////////////////////////////////////////////////////
  def dumpRom(self):
    """
    Dump a ROM
    """
    ### Begin a ROM dump
    self.log('Starting ROM dump')
    self.lockGui()


    if self.bankSwitchMethod == BankSwitchMethod.NONE:
      self.rom.setSize(4096)
      self.sync()

      for i in range(0,16):
        data = self.readBlock(0x1000 + i * 256, 256)
        self.rom.write(i * 256, data)

      self.rom.setValid(True)

    elif self.bankSwitchMethod == BankSwitchMethod.F8:
      self.rom.setSize(8192)
      self.sync()

      data = self.read(0x1FF8)

      for i in range(0,16):
        data = self.readBlock(0x1000 + i * 256, 256)
        self.rom.write(i * 256, data)

      for i in range(0,16):
        data = self.readBlock(0x1000 + i * 256, 256)
        self.rom.write(i * 256 + 0x1000, data)

      self.rom.setValid(True)


    else:
      self.log('Bankswitch method not implemented.')

    self.unlockGui()

    ### Dumped the ROM succesfully
    self.log('Done! Rom has been dumped succesfully.')


  def saveDump(self, name, rom = None):
    """
    Save ROM dump to a file 
    :param name: Name/path to file.
    :type name: str
    """

    if rom is None:
      rom = self.rom

    if rom.isValid():
      self.log('Saving ROM to file.')
      try:
        with open(name, 'wb+') as f:
          f.write(bytes(rom))

      except IOError as e:
        self.log('Could not write to file.')
        self.debugLog('IOError: (' + e.errno + '): '  + e.strerror)


  def scanSerial(self):
    ports = self.fw.scan()
    return ports

  def setSerialPort(self, port, timeout):
    """ Set serial port.
    :return: True when port was opened
    :rtype: bool """
    retv = False

    if port:
      if self.fw.open(port, timeout):
        self.log('Opened serial port ' + port)
        retv = True
      else:
        self.log('Could not open serial port ' + port)

    return retv


  def sync(self):
    """ Synchronize with firmware """
    self.fw.sync()


  def read(self, address):
    """ Read single byte
    :rtype: bytes """
    #todo check address
    request = Fw_Packet(Fw_Command.READ_SINGLE, address=address)
    reply = self.fw.transceive(request)
    data = reply.getData()

    if len(data) != 1:
      raise BaseException('Bug: asked for single byte, got ' + str(len(data)) + ' byte(s).')

    return data


  def readBlock(self, address, length):
    """ Read block
    :rtype: bytes """
    # TODO check length

    request = Fw_Packet(Fw_Command.READ_BLOCK, address = address, length = length)
    reply = self.fw.transceive(request)
    data = reply.getData()

    if len(data) != length:
      raise BaseException('Bug: asked for ' + str(length) + ' byte(s), got ' + str(len(data)) + ' byte(s).')

    return data


if __name__ == '__main__':
  import sys
  from emulator import *

  parser = argparse.ArgumentParser(description='VCS ROM dumping utility')
  parser.add_argument('-o', dest = 'filename', default = '.tmp.a26')
  parser.add_argument('-p', dest = 'port')
  parser.add_argument('-l', dest = 'list', help = 'List available devices.')
  parser.add_argument('-a', dest = 'autoLaunch', help = 'Launch emulator')
  args = parser.parse_args()

  rc = RomClient(None)
  
  # Scan and list serial ports
  ports = rc.scanSerial()
  if args.list:
    print('Available serial ports:')
    for i,port in iterate(ports):
      print(i, ':', port.device)
    sys.exit()

  # Auto detect device
  ready = False
  if args.port is None:
    for port in ports:
      if '/dev/ttyACM' in port.device:
        if rc.setSerialPort(port.device, 3):
          #TODO do some kind of handshake with the device to verify its compatibility
          ready = True
          break
  else:
    if rc.setSerialPort(args.port, 3):
      ready = True

  if not ready:
    print('Could not open device.')
    sys.exit()

  # Dump rom and save to file
  rc.dumpRom()
  rc.saveDump(args.filename)

  # Auto launch emulator
  if args.autoLaunch:
    self.emu = Emulator()
    self.emu.launch(args.filename)
