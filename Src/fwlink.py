import serial

class Fw_Link():
  """ Communicate with firmware through serial port """

  def __init__(self, port = None):
    self.open(port)
    

  def open(self, port):
    """ 
    Open a serial port for communication with the firmware.
    :param name: The name of the serial port e.g. /dev/ttyS0.
    :return: True if port was opened
    :rtype: bool
    """
    retv = False

    if port is not None:
      try:
        self.ser = serial.Serial(port)
        self.ser.timeout = 0.1
        self.ser.flushInput()
        self.ser.flushOutput()

        retv = True  
      except serial.SerialException:
        pass

    return retv

  def close(self):
    """
    Close serial port.
    """
    if self.ser is not None:
      self.ser.close()

  def write(data):
    """
    Write data to the firmware.
    :param data: Data.
    :type data: bytes 
    :return: True if data was written
    :rtype: bool
    """
    if self.ser is not None:
      try:
        self.ser.write(data)
      except serial.SerialException as e:
        return False
      return True

  def read(len):
    """
    Read data from the firmware.
    :param len: Data length.
    :return: Received data. Can be less bytes than requested if a timeout occured.
    :rtype: bytes
    """
    data = b''
    success = False

    if self.ser is not None:
      try:
        data = self.ser.read(500)
        success = True
      except serial.SerialException as e:
        pass

    return success, data
