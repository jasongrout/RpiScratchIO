import string, spidev
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
  def config(self,options):
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
    if len(self.inputChannels) == 0:
      return None

    sensorValues = {}
    if len(self.inputChannels) == 1:
      sensorValues[self.deviceName] = 0
    else:
      sensorValues = {}
      for channelId in self.inputChannels:
        sensorValues[self.deviceName+":"+str(channelId)] = 0

      # Tell scratch about all of the input channels in one message.
      print sensorValues
      self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate(sensorValues)
        

#--------------------------------------

class GpioDevice(GenericDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(GpioDevice, self).__init__(deviceName_,rpiScratchIO_,connections_)
    self.rpiScratchIO.rpiGpioConnections.requestGpioIds(self.deviceName,self.connections)

  def cleanup(self):
    if self.configured:
      self.rpiScratchIO.gpioCleanUp = True

#--------------------------------------

class SimpleGpio(GpioDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(SimpleGpio, self).__init__(deviceName_,rpiScratchIO_,connections_)
    self.bcmId = int(string.replace(self.connections[0],'GPIO',''))
    self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate({self.deviceName:0}) # Add to Scratch

  def config(self,options):
    exec("GPIO.setup(%d,%s)" % (self.bcmId, options))
    self.configured = True

  def read(self): # to add this
    if not self.configured: # use the default options
      self.config("GPIO.IN")
    value = int(GPIO.input(self.connections[0]))
    self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate({self.deviceName:value})

  def write(self,value): # to add this
    if not self.configured: # use the default options 
      self.config("GPIO.OUT")
    print "GPIO.output(%d,%d)" % (self.bcmId, int(value))
    GPIO.output(self.bcmId,int(value))

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
    super(FileConnection, self).__init__(deviceName_,rpiScratchIO_,connections_)

  def config(self,options):
    if self.configured:
      return None
    self.file = open(self.connections[0], options)
    if options.find("w"):
      self.write = True
      self.read = False
    if options.find("r+"):
      self.write = True
      self.read = True
    else:
      self.write = False
      self.read = True
    self.configured = True

  def cleanup(self):
    if self.configured:
      self.file.close()

  def read(self,channelId):
    if not self.configured: # Use default read option
      self.config('r')
    if not self.read:
      raise Exception("File is open for output only")

  def write(self,channelId,value):
    if not self.configured: # Use default write option
      self.config('w')
    if not self.write:
      raise Exception("File is open for input only") 
    self.file.write(value)


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
    print "read=%s" % r
    value = ((r[1]&3) << 8) + r[2]
    sensorName = "%s:%d" % (self.deviceName,channelNumber)
    self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate({sensorName:value})

