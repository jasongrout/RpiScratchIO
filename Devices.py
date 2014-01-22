import spidev

class NoSuchChannel(Exception):
  pass

#--------------------------------------

class GenericDevice(object):

  def __init__(self,deviceName_,scratchHandler_):
    self.deviceName = deviceName_
    self.inputChannels = []
    self.outputChannels = []
    self.configured = False
    self.scratchHandler = scratchHandler_

  """Need to implement this in the derived class."""
  def configure(self,options):
    raise NotImplementedError("No configure method available")

  """Need to implement this in the derived class."""
  def read(self,channelId):
    raise NotImplementedError("No read method available")

  """Need to implement this in the derived class."""
  def write(self,channelId,value):
    raise NotImplementedError("No write method available")

  """Check if the channel number is in the list of available input
  channel numbers."""
  def validInputChannel(self,channelId):
    if not channel in self.inputChannels:
      raise NoSuchChannel

  """Check if the channel number is in the list of available output
  channel numbers."""
  def validOutputChannel(self,channelId):
    if not channel in self.outputChannels:
      raise NoSuchChannel

  """Announce to Scratch that the inputs exist as remote sensors"""
  def addSensors(self):
    if len(inputChannels) == 0:
      return None

    sensorValues = {}
    if len(inputChannels) == 1:
      sensorValues["self.deviceName"] = 0
    else:
      sensorValues = {}
      for channelId in inputChannels:
        sensorValues["self.deviceName:"+str(channelId)] = 0

    self.scratchHandler.updateSensors(sensorValues) # check if this pairing is right
        

#--------------------------------------

class GpioDevice(GenericDevice):

  def __init__(self,deviceName_,scratchHandler_,gpioInterface_):
    super(GenericDevice, self).__init__(deviceName_,scratchHandler_)
    self.rpiGpioInterface = gpioInterface_
    self.gpioIds = [] # Associated pins

  def requestGpioIds(self):
    return self.rpiGpioInterface.requestGpioIds(self.gpioIds, self.deviceName)

#--------------------------------------

class SimpleGpio(GpioDevice):

  def __init__(self,deviceName_,scratchHandler_,gpioInterface_,gpioId_):
    super(GenericDevice, self).__init__(deviceName_,scratchHandler_,gpioInterface_)
    self.gpioIds = [gpioId_]
    
    # Request this pin
    self.requestGpioIds()

  def read: # to add this

  def write: # to add this

#--------------------------------------

class SpiDevice(GpioDevice):

  def __init__(self,deviceName_,scratchHandler_,gpioInterface_,spiChannel_,spiDevice_):
    super(SpiDevice, self).__init__(deviceName_,scratchHandler_,gpioInterface_)
    self.spiChannel = spiChannel_
    self.spiDevice = spiDevice_

    # Get the list of GPIO ids involved
    self.gpioIds = self.rpiGpioInterface.getPinList(self.spiChannel, self.spiDevice)

    # Request these pins
    self.requestGpioIds()

    # Create a SPI connection
    self.spi = spidev.SpiDev() 
    self.spi.open(spiChannel,spiDevice)

  def __del__(self):
    self.spi.close()

#--------------------------------------

class FileConnection(GenericDevice):
  def __init__(self,deviceName_,scratchHandler_,read_=True):
    super(GenericDevice, self).__init__(deviceName_,scratchHandler_)
    self.read = read_
    if self.read:
      accessType = 'r'
    else:
      accessType = 'w'

    # Open file connection
    self.file = open(self.deviceName, accessType) # Need to catch when this fails

    # Add this sensor to Scratch (if file is open)
    #if self.read:
      

  def read(self,channelId):
    if not self.read:
      raise NotImplementedError("No read method available") # need better exception

  """Need to implement this in the derived class."""
  def write(self,channelId,value):
    if self.read:
      raise NotImplementedError("No write method available") # need better exception



#========================================
#
# These are particular chips and examples of how to use the base
# classes.

class MCP3008(SpiDevice):

  def __init__(self,scratchHandler_,gpioInterface_,spiChannel_,spiDevice_):
    super(MCP3008, self).__init__("MCP3008",scratchHandler_,gpioInterface_,spiChannel_,spiDevice_)
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

