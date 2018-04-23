from emulator import *
import rom as ROM
import argparse
from subprocess import Popen

kSerialRxTimeout = 1 #s
kEmulatorPath = 'stella'

def _debugPrint(message):
  print('___debug__ ' + message)


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


def launch(executable, args):
  if executable and args:
    return Popen([executable, args])
  

def dumpRom(fwlink, bankswitching = BankSwitchMethod.NONE):
  """
  Dump a ROM
  :return: Dumped rom
  :rtype: Rom
  """

  rom = ROM.Rom()
  fw = fwlink

  if bankswitching == BankSwitchMethod.NONE:
    rom.setSize(4096)
    fw.sync()

    for i in range(0,16):
      data = fw.readBlock(0x1000 + i * 256, 256)
      rom.write(i * 256, data)

    rom.setValid(True)

  elif bankswitching == BankSwitchMethod.F8:
    rom.setSize(8192)
    fw.sync()

    data = fw.read(0x1FF8)

    for i in range(0,16):
      data = fw.readBlock(0x1000 + i * 256, 256)
      rom.write(i * 256, data)

    for i in range(0,16):
      data = fw.readBlock(0x1000 + i * 256, 256)
      rom.write(i * 256 + 0x1000, data)

    rom.setValid(True)

  return rom

def saveDump(name, rom):
  """
  Save ROM dump to a file 
  :param name: Name/path to file.
  :param rom: ROM dump to save
  :type name: str
  :type rom: Rom
  """
  success = False
  if rom:
    with open(name, 'wb+') as f:
      try:
        d = bytes(rom)
        try: 
          f.write(d)
          success = True
        except IOError:
          pass
      except BufferError:
        pass

  return success

def scanSerial(fwlink):
  return fw.scan()

if __name__ == '__main__':
  import sys
  from fwlink import *

  parser = argparse.ArgumentParser(description='VCS ROM dumping utility')
  parser.add_argument('-o', dest = 'filename', default = '.tmp.a26')
  parser.add_argument('-p', dest = 'port')
  parser.add_argument('-l', dest = 'list', action = 'store_true', help = 'List available devices.')
  parser.add_argument('-a', dest = 'autoLaunch', action = 'store_true', help = 'Launch emulator')
  args = parser.parse_args()
  
  # Scan and list serial ports
  fw = Fw_Link()
  ports = scanSerial()
  if args.list:
    print('Available serial ports:\n')
    for i,port in enumerate(ports):
      print('*\t', port.device)
    print('')
    sys.exit()

  # Auto detect device
  if args.port is None:
    for port in ports:
      if '/dev/ttyACM' in port.device:
        try:
          # Attempt to open port
          fw.open(port.device, kSerialRxTimeout) #TODO refactor
          #TODO verify link with handshake
          break
        except IOError as e:
          print(e.strerror)
  else:
    try:
      fw.open(args.port, kSerialRxTimeout) #TODO refactor
    except IOError as e:
      print(e.strerror)

  if not fw.isOpen():
    print('Could not establish firmware link.')
    sys.exit()

  # Dump rom and save to file
  print('Starting ROM dump')
  rom = dumpRom(fw)

  if rom.isValid():
    print('Rom has been dumped succesfully')
  else:
    print('Dump failed')
    sys.exit()

  print('Saving ROM dump to file')
  saveDump(args.filename, rom) #TODO check if file can be created before dumping

  # Auto launch emulator
  if args.autoLaunch:
    print('Launching emulator')
    launch(kEmulatorPath, args.filename)
