""" 
  Romclient
  ROM dumping utility
  """

import rom as ROM
import argparse
from subprocess import Popen

kSerialRxTimeout = 2 # unit: s
kEmulatorPath = 'stella' # TODO make argparse argument

def _debugPrint(message):
  print('___debug__ ' + message)


def _nop():
  """ No operation. """
  pass


def launch(executable, args):
  if executable and args:
    return Popen([executable, args])
  

def dumpRom(fwlink, bankswitching = 'none'):
  """
  Dump a ROM

  === Bankswitching types ===
  Special thanks to Kevin "Kevtris" Horton for these descriptions

  :param bankswitching: Bankswitching schemes include:
                      'none' No bankswitching.
        not implemented 'f6' FF6/FF7/FF8/FF9 bankswitching
                        'f8' FF8/FF9 bankswitching
        not implemented 'fa' FF8/FF9/FFA bankswitching (aka CBS' RAM Plus)
        not implemented 'e0' FE0-FF7 bankswitching (aka Parker Bros.)
        not implemented 'e7' FE0-FE7 bankswitching found on M-Network carts
        not implemented 'fe' 01FE/11FE bankswitching (aka Activision Robot Tank)
  :type bankswitching: str
  :return: Dumped rom
  :rtype: Rom
  """

  rom = ROM.Rom()
  fw = fwlink

  # TODO create some kind of configuration file for defining bankswitching schemes

  if bankswitching == 'none':
    rom.setSize(4096)
    #fw.sync()

    for i in range(0,16):
      data = fw.readBlock(0x1000 + i * 256, 256)
      rom.write(i * 256, data)

    rom.setValid(True)

  elif bankswitching == 'f8':
    rom.setSize(8192)
    #fw.sync()

    # Switch to bank0 by reading from hotspot 1FF8
    fw.read(0x1FF8)

    # Read bank
    for i in range(0,16):
      data = fw.readBlock(0x1000 + i * 256, 256)
      rom.write(i * 256, data)    

    # Switch to bank1 by reading from hotspot 1FF9
    data = fw.read(0x1FF9)

    for i in range(0,16):
      data = fw.readBlock(0x1000 + i * 256, 256)
      rom.write(i * 256 + 0x1000, data)

    # Read some data near the hotspots
    fw.read(0x1FF8)
    rom.write(0x0FF8, fw.read(0x1FF8))
    rom.write(0x0FFA, fw.readBlock(0x1FFA, 6))
    fw.read(0x1FF9)
    rom.write(0x1FF9, fw.read(0x1FF9))
    rom.write(0x1FFA, fw.readBlock(0x1FFA, 6))

    rom.setValid(True)
  else:
      raise ValueError("Unsupported bankswitching method " + bankswitching)

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
  parser.add_argument('-b', dest = 'switchMethod', help = 'Bankswitching method', choices=['none', 'f6', 'f8', 'fa', 'e0', 'e7', 'fe'], default='none')

  args = parser.parse_args()
  
  # Scan and list serial ports
  fw = Fw_Link()
  ports = scanSerial(fw)
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
    print('Could not connect to device.')
    sys.exit()

  # Dump rom and save to file
  print('Starting ROM dump')
  rom = dumpRom(fw, args.switchMethod)

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
