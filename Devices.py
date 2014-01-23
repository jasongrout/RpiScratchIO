import spidev
import RPi.GPIO as GPIO

class NoSuchChannel(Exception):
  pass

#--------------------------------------

class GenericDevice(object):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    self.deviceName = deviceName_
    self.inputChannels = []
    self.outputChannels = []
    self.configured = False
    self.rpiScratchIO = rpiScratchIO_
    self.connections = connections_

  """Since Python does not always call the destructor"""
  def cleanup(self):
    pass

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
        self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate(sensorValues)
        

#--------------------------------------

class GpioDevice(GenericDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(GpioDevice, self).__init__(deviceName_,rpiScratchIO_,connections_)

  def cleanup(self):
    if self.configured:
      self.rpiScratchIO.gpioCleanUp = True

  def requestGpioIds(self):
    print "Requesting %s" % self.connections
    #return self.rpiGpioInterface.requestGpioIds(self.gpioIds, self.deviceName)

#--------------------------------------

class SimpleGpio(GpioDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(SimpleGpio, self).__init__(deviceName_,rpiScratchIO_,connections_)
    self.requestGpioIds() # Request connections

  def read(self): # to add this
    return int(GPIO.input(self.connections[0]))

  def write(self): # to add this
    GPIO.output(self.connections[0],bool(value))

#--------------------------------------

class SpiDevice(GpioDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(SpiDevice, self).__init__(deviceName_,rpiScratchIO_,connections_)
    if len(self.connections) != 1:
      Exception("SPI device %s must have one connection to SPI0 or SPI1" % self.deviceName)
    if self.connections[0] == "SPI0":
      spiDevice = 0
    elif self.connection[0] == "SPI1":
      spiDevice = 1
    else:
      Exception("SPI device %s must have one connection to SPI0 or SPI1" % self.deviceName)
      
    spiChannel = 0

    # Get the list of GPIO ids involved
    #self.gpioIds = self.rpiGpioInterface.getPinList(self.spiChannel, self.spiDevice)

    # Request these pins
    #self.requestGpioIds()

    # Create a SPI connection
    self.spi = spidev.SpiDev() 
    self.spi.open(spiChannel,spiDevice)

  def cleanup(self):
    self.spi.close()

#--------------------------------------

class FileConnection(GenericDevice):
  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(FileConnection, self).__init__(deviceName_,rpiScratchIO_,connections__)
    
    #self.read = read_
    #if self.read:
    #  accessType = 'r'
    #else:
    #  accessType = 'w'

    # Open file connection
    #self.file = open(self.deviceName, accessType) # Need to catch when this fails

    # Add this sensor to Scratch (if file is open)
    #if self.read:

  def cleanup(self):
    if self.configured:
      self.file.close()

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

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(MCP3008, self).__init__(deviceName_,rpiScratchIO_,connections_)
    for i in xrange(8):
      self.inputChannels += [i]

  def read(self,channelNumber):
    self.validInputChannel(channelNumber)
    r = self._spi.xfer2([1,(8+channelNumber)<<4,0])
    print r
    #adcout = ((r[1]&3) << 8) + r[2]
    #return adcout

