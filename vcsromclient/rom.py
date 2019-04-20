
def isPowerOfTwo(value):
  """ Check if value is power of two. Works for floats as well as integer types.
  http://graphics.stanford.edu/~seander/bithacks.html#DetermineIfPowerOf2
  :return: True if value is power of two.
  :rtype: bool """
  v = int(value)
  if v != value:
    return False
  
  return (v & (v - 1)) == 0

def overwrite(dst, index, src):
  return dst[:index] + src + dst[index + len(src):]

class Rom():
  """ ROM storage class 
  Attributes:
    _kRomStart  ROM start address in 6508 address space
  """
  kRomStart = 0x1000

  def __init__(self, size = 4096): # TODO avoid magic numbers. 4096 is size of common 4KB ROM
    self.setValid(False)
    self.setSize(size)


  def write(self, offset, data):
    if data is not None:
      if offset > self.size:
        raise IndexError('Offset is outside of ROM.')
      self.data = overwrite(self.data, offset, data)
      self.valid = False


  def setValid(self, valid): #TODO keep a shadow copy of a rom to check if all memory locations have been written to.
    self.valid = valid


  def isValid(self):
    return self.valid


  def getSize(self):
    return self.size


  def setSize(self, size):
    """ Set the size of the ROM
    Warning: Clears ROM content """
    if not isPowerOfTwo(size):
      raise ValueError('ROM size must be power of 2.')
    
    self.size = size
    self.data = bytes(self.size)
    self.valid = False


  def __bytes__(self):
    if not self.valid:
      raise BufferError('Trying to access invalid ROM')
    return bytes(self.data)


  def __bytearray__(self):
    if not self.valid:
      raise BufferError('Trying to access invalid ROM')
    return self.data