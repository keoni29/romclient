import struct

class Fw_Command:
  """
  Firmware command

  Attributes:
    READ_SINGLE	 	Read from a single memory address
    WRITE_SINGLE	Write to a single memory address TODO implement
    EMULATE_SINGLE	Emulate reading from a single memory address TODO implemenent
    READ_BLOCK	 	Read a block of memory
    WRITE_BLOCK	 	Write a block of memory TODO implement
    EMULATE_BLOCK	Emulate reading from a block of memory TODO implement
    SET_READ_DELAY	Set the delay between reads in ms TODO implement
    GET_READ_DELAY	Get the delay between reads in ms TODO implement
    GET_INFO	 	Get firmware/hardware version info
    SYNC	 		Synchronizes soft and firmware by resetting the interpreter. Synchronization character, not an actual command.
  """

  READ_SINGLE = ord('r') # TODO define as numbers rather than using ord().
  WRITE_SINGLE = ord('w')
  EMULATE_SINGLE = ord('e')
  READ_BLOCK = ord('R')
  WRITE_BLOCK = ord('W')
  EMULATE_BLOCK = ord('E')
  SET_READ_DELAY = ord('d')
  GET_READ_DELAY = ord('D')
  GET_INFO = ord('I')
  SYNC = ord('S')
  NOP = ord('n')

class Fw_Packet:
  """ Firmware packet """
  _HEADER_LENGTH = 10

  def __init__(self, cmd = Fw_Command.NOP, status = 0, address = 0, data = bytes(), length = 0, requestLength = None, replyLength = None): 
    self.cmd = cmd # Todo check type of cmd
    self.setLength(length)
    self.setAddress(address)

    if replyLength is not None:
      self.replyLength = replyLength
    if requestLength is not None:
      self.requestLength = requestLength

    self.setData(data)
    self.status = status
  
  def setData(self, data):
    self.data = data

  def getData(self):
    return self.data

  def setAddress(self, address):
    self.address = address
    #TODO limit to 16-bit

  def addressNextBlock(self):
    """ Increment address by transfer length. """
    self.address += self._length

  def setLength(self, length):
    """ Set transfer length in bytes """
    self._length = length
    self.requestLength = 0
    self.replyLength = 0
    #TODO limit to 16-bit

    if self.cmd == Fw_Command.READ_SINGLE:
      self.replyLength = 1
    elif self.cmd == Fw_Command.READ_BLOCK:
      self.replyLength = self._length

  def getReplyPacketLength(self):
    """ Get length of request and reply 
    :return: requestLength, replyLength
    :rtype: tuple """
    return self.replyLength + self._HEADER_LENGTH

  # def __str__(self):
  #   encoded_request = self._encode()
  #   return ' '.join(format(x, '02x') for x in encoded_request)

  def print(self, print_data = False):
    print('cmd :', self.cmd, '\'' + str(chr(97)) + '\'') 
    print('status :', self.status)
    print('requestLength :', self.requestLength)
    print('replyLength :', self.replyLength)
    print('address :', hex(self.address))
    if print_data:
      print('data :', ' '.join(format(x, '02x') for x in self.data))


  def __encode(self):
    # Two passes: First pack and calculate checksum, then pack with correct checksum
    checksum = 0
    for _ in range(2):
      header = (
        self.cmd,
        self.status,
        self.requestLength,
        self.replyLength,
        self.address,
        checksum,
      )

      fmt = '<B B H H H H'
      packet = header
      if len(self.data):
        packet += (self.data,)
        fmt += ' p'

      s = struct.Struct(fmt)
      encoded_packet = s.pack(*packet)
      checksum = sum(encoded_packet)

    return encoded_packet, checksum

  def _encode(self):
    """ Encode package
    :return: Encoded packet
    :rtype: bytes """
    
    encoded_packet,_ = self.__encode()

    return encoded_packet

  def _getChecksum(self):
    _, checksum = self.__encode()
    return checksum


def decodeFwPacket(encoded_packet):
    """ Create packet from encoded data """

    if len(encoded_packet) < Fw_Packet._HEADER_LENGTH:
      return None #TODO length exception?

    # TODO clean up code and make more readable
    fmt = '<B B H H H H'
    verifyChecksum = sum(encoded_packet[0:8])
    data = bytes()
    if len(encoded_packet) > Fw_Packet._HEADER_LENGTH:
      data = encoded_packet[10:]
      verifyChecksum += sum(data)

    verifyChecksum &= 0x00FFFF
    packet = struct.unpack(fmt, encoded_packet[0:10])

    cmd = packet[0]
    status = packet[1]
    requestLength = packet[2]
    replyLength = packet[3]
    address = packet[4]
    checksum = packet[5]

    if verifyChecksum != checksum:
      return None #TODO checksum exception?

    p = Fw_Packet(\
      cmd = cmd, status = status, requestLength = requestLength, \
      replyLength = replyLength, address = address, \
      data = data)
    return p

