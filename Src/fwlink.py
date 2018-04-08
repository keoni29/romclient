import serial

class Fw_Link():
  """ Communicate with firmware through serial port """

  def __init__(self, port = None):
    self.open(port, 0)
    

  def open(self, port, readtimeout):
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


  def write(self, data):
    """
    Write data to the firmware.
    :param data: Data.
    :type data: bytes 
    :return: success, errorstr. success is True if data was written
    :rtype: bool, str
    """
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


  def read(self, len):
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
        data = self.ser.read(len)
        success = True
      except serial.SerialException as e:
        pass

    return success, data
