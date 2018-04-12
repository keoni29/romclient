from fwlink import *

class Cartridge():
  """ Abstraction layer around cartridge reader firmware. Provides random access to game cartridge. """
  def __init__(self):
    # Set up firmware link
    self.setSerialReadTimeout(1)
    self.fw = Fw_Link()
    self.setSerialPort(port)
    self.setBankSwitchMethod(BankSwitchMethod.NONE)

    self.clear()
  
  def read(self, address, len):
    success,data = self.fw.read(self._kMaxReadSize)
    length = len(data)
    return success,data

  def clear(self):
    self.data = bytearray()