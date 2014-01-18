import spidev

class NoSuchChannel(Exception):
  pass

class BusDevice(object):

  def __init__(self,deviceName):
    self._deviceName = deviceName
    self._inputChannels = []
    self._outputChannels = []
    self._deviceName = "None"

  def inputChannels(self):
    return self._inputChannels

  def validInputChannel(self,channel):
    if not channel in self._inputChannels:
      raise NoSuchChannel

  def validOutputChannel(self,channel):
    if not channel in self._outputChannels:
      raise NoSuchChannel

#--------------------------------------

class SpiDevice(BusDevice):

  def __init__(self,deviceName,spiChannel,spiDevice):
    super(SpiDevice, self).__init__(deviceName)
    self._spiChannel = spiChannel
    self._spiDevice = spiDevice
    self._spi = spidev.SpiDev() 
    self._spi.open(spiChannel,spiDevice)

  def __del__(self):
    self._spi.close()

#----------------------------------------

class MCP3008(SpiDevice):

  def __init__(self,spiChannel,spiDevice):
    super(MCP3008, self).__init__("MCP3008",spiChannel,spiDevice)
    for i in xrange(8):
      self._inputChannels += [i]

  def read(self,channelNumber):
    self.validInputChannel(channelNumber)
    r = self._spi.xfer2([1,(8+channelNumber)<<4,0])
    print r
    #adcout = ((r[1]&3) << 8) + r[2]
    #return adcout

  def __del__(self):
    super(MCP3008,self).__del__()
