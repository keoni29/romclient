import serial

from fwpacket import *

#-------------------------------------------------------------------------------
class Fw_Link():
  """ Communicate with firmware through serial port """

  def __init__(self, port = None):
    self.open(port, 0)
    

  def open(self, port, readtimeout):
    """ Open a serial port for communication with the firmware.
    :param name: The name of the serial port e.g. /dev/ttyS0.
    :return: True if port was opened
    :rtype: bool """
    retv = False

    if port is not None:
      try:
        self.ser = serial.Serial(port)
        self.ser.timeout = readtimeout
        # Use common baud rate (Almost 1 MB/s)
        # When using USB CDC (virtual COM port) any baud rate can be used.
        # The limit is about 1 MB/s with fast firmware
        self.ser.baudrate = 921600
        self.ser.flushInput()
        self.ser.flushOutput()

        retv = True  
      except serial.SerialException as e:
        print("Serial error: (", e.errno, "):", e.strerror)

    return retv


  def close(self):
    """
    Close serial port.
    """
    if self.ser is not None:
      self.ser.close()

  def transceive(self, request_packet):
    """ Transmit request packet
    :type firmware_command: Fw_Packet  
    :return: Reply packet
    :rtype: Fw_Packet """

    encoded_request = request_packet._encode()
    success,_ = self._write(encoded_request)
    
    reply = None
    if success:
      expectedLength = request_packet.getReplyPacketLength()
      success,encoded_reply = self._read(expectedLength)
      
      if success:
        actualLength = len(encoded_reply)
        if actualLength == 0:
          raise IOError('Did not receive reply packet')
        elif actualLength < expectedLength:
          raise IOError('Did not receive full reply packet')

        reply = decodeFwPacket(encoded_reply)

      return reply

  def sync(self):
    """ Synchronize communication with firmware
    :rtype: bool """
    SYNC = b'S' #TODO Define these in Fw_Command
    NULL = b'\x00'
    request = SYNC * 13 + NULL #TODO wait for acknowledgement (Also TODO firmware send ack after sync)
    success, errorstr = self._write(request)
    return success

  def _write(self, data):
    """ Write data to the firmware.
    :param data: Data.
    :type data: bytes 
    :return: success, errorstr. success is True if data was written
    :rtype: bool, str """
    success = False
    errorstr = ''

    if self.ser is not None:
      try:
        self.ser.write(data)
        self.ser.flush()
        success = True
      except serial.SerialException as e:
        errorstr = e.strerror
      except serial.SerialTimeoutException as e:
        errorstr = e.strerror
    
    return success, errorstr


  def _read(self, len):
    """ Read data from the firmware.
    :param len: Data length.
    :return: success, data Can be less bytes than requested if a timeout occured.
    :rtype: boolean, bytes """
    data = b''
    success = False

    if self.ser is not None:
      try:
        data = self.ser.read(len)
        success = True
      except serial.SerialException as e:
        pass

    return success, data
