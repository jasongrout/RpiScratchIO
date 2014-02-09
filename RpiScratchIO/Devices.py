import string, spidev
import RPi.GPIO as GPIO

#=====================================

class GenericDevice(object):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    self.deviceName = deviceName_
    self.inputChannels = []
    self.outputChannels = []
    self.configured = False
    self.rpiScratchIO = rpiScratchIO_
    self.connections = connections_

  #-----------------------------

  """Since Python does not always call the destructor"""
  def cleanup(self):
    pass

  #-----------------------------

  """Need to implement this in the derived class."""
  def config(self,argList):
    print("WARNING: \"%s\" does not contain a \"config\" function." % self.deviceName)
    return None

  #-----------------------------

  """Need to implement this in the derived class."""
  def read(self,channelId):
    print("WARNING: \"%s\" does not contain a \"read\" function." % self.deviceName)

  #-----------------------------

  """Need to implement this in the derived class."""
  def write(self,channelId,value):
    print("WARNING: \"%s\" does not contain a \"write\" function." % self.deviceName)

  #-----------------------------

  """Check if the channel number is in the list of available input
  channel numbers."""
  def validInputChannel(self,channelId):
    try:
      channelNumber = int(channelId)
    except ValueError:
      print("WARNING: \"%s\" is not a channel number", channelId)
      return -1

    if not channelNumber in self.inputChannels:
      print("WARNING: \"%s\" does not have an input channel number %d" % self.deviceName, channelNumber)
      return -1

    return channelNumber

  #-----------------------------

  """Check if the channel number is in the list of available output
  channel numbers."""
  def validOutputChannel(self,channelId):
    try:
      channelNumber = int(channelId)
    except ValueError:
      print("WARNING: \"%s\" is not a channel number", channelId)
      return -1

    if not channelNumber in self.outputChannels:
      print("WARNING: \"%s\" does not have an output channel number %d" % self.deviceName, channelNumber)
      return -1

    return channelNumber

  #-----------------------------

  """Check if the value is a number"""
  def isNumber(self,value,requireInt=False):
    if not isinstance(value, (int, long, float)):
      print("WARNING: \"%s\" is not a number.  Device \"%s\" expects a numerical value" % (value,self.deviceName))
      return False
    if requireInt and not isinstance(value, (int, long)):
      print("WARNING: \"%s\" is not an integer.  Device \"%s\" expects an integer value" % (value,self.deviceName))
      return False
    return True

  #-----------------------------

  """Announce to Scratch that the inputs exist as remote sensors"""
  def addSensors(self):
    if len(self.inputChannels) == 0:
      return None

    sensorValues = {}
    if len(self.inputChannels) == 1:
      sensorValues[self.deviceName] = 0
    else:
      for channelId in self.inputChannels:
        sensorValues[self.deviceName+":"+str(channelId)] = 0

      # Tell Scratch about all of the input channels in one message.
      #print sensorValues
      self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate(sensorValues)

  #-----------------------------

  """Update sensor value in Scratch"""
  def updateSensor(self,channelId,value):
    if not isinstance(value, (int, long, float)):
      print("WARNING: device \"%s\" attempted to send \"%s\" to a Scratch.  This is not a number and was ignored" % self.deviceName, value)
      return None

    sensorValues = {}
    if len(self.inputChannels) == 1:
      sensorValues[self.deviceName] = value
    else:
      sensorValues[self.deviceName+":"+str(channelId)] = value

    # Tell Scratch about this sensor value
    self.rpiScratchIO.scratchHandler.scratchConnection.sensorupdate(sensorValues)

  #-----------------------------

  """Send a broadcast message to Scratch in a standard form for a trigger"""
  def broadcastTrigger(self,channelId):
    print "FIX ME!"

#=====================================

class GpioDevice(GenericDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(GpioDevice, self).__init__(deviceName_,rpiScratchIO_,connections_)
    self.rpiScratchIO.rpiGpioConnections.requestGpioIds(self.deviceName,self.connections)

  #-----------------------------

  def cleanup(self):
    if self.configured:
      self.rpiScratchIO.gpioCleanUp = True

#=====================================

class SimpleGpio(GpioDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(SimpleGpio, self).__init__(deviceName_,rpiScratchIO_,connections_)
    self.bcmId = int(string.replace(self.connections[0],'GPIO',''))
    self.inputChannels += [0] # Has just one channel
    self.addSensors() # Add to Scratch

  #-----------------------------

  def config(self,argList):
    nargs = len(argList)
    if nargs == 0:
      print("WARNING: \"config\" expects at least one argument.  No arguments were given")
      return None
      
    #print "config %s" % argList

    if argList[0] == "in":
      if nargs == 1:
        GPIO.setup(self.bcmId,GPIO.IN)
      else:
        if argList[1] == "pullup":
          GPIO.setup(self.bcmId,GPIO.IN,GPIO.PUD_UP)
        elif argList[1] == "pulldown":
          GPIO.setup(self.bcmId,GPIO.IN,GPIO.PUD_DOWN)
    elif argList[0] == "out":
      GPIO.setup(self.bcmId,GPIO.OUT)
    elif argList[0] == "callback":
      if nargs == 1:
        print("WARNING: device %s expects \"callback,rising\",\"callback,falling\" or \"callback,both\"")
        return None
      if argList[1] == 'rising':
        GPIO.add_event_detect(self.bcmId, GPIO.RISING, callback=self.gpioCallBack, bouncetime=200) 
      elif argList[1] == 'falling':
        GPIO.add_event_detect(self.bcmId, GPIO.FALLING, callback=self.gpioCallBack, bouncetime=200)
      elif argList[1] == 'both':
        GPIO.add_event_detect(self.bcmId, GPIO.BOTH, callback=self.gpioCallBack, bouncetime=200)
      else:
        print("WARNING: device %s expects \"callback,rising\",\"callback,falling\" or \"callback,both\"")
        return None
    else:
      print("WARNING: config arguments %s not recognised by device %s" % argList, self.deviceName)
      return None

    self.configured = True

  #-----------------------------

  def read(self,channelId): # to add this
    if not self.configured: # use the default options
      self.config(["in"])
    value = int(GPIO.input(self.bcmId))
    self.updateSensor(channelId,value)

  #-----------------------------

  def write(self,channelId,value): # to add this
    if not self.configured: # use the default options 
      self.config(["out"])
    #print "GPIO.output(%d,%d)" % (self.bcmId, int(value))
    GPIO.output(self.bcmId,int(value))
    self.updateSensor(channelId,value)

  #-----------------------------

  def gpioCallBack(self,channelId):
    # Update the value
    self.read(0) # There is only one channel in this GPIO object
    
    # Broadcast message to Scratch
    broadcast_msg="%s:trig" % self.deviceName
    #print broadcast_msg
    self.rpiScratchIO.scratchHandler.scratchConnection.broadcast(broadcast_msg)

#=====================================

class SpiDevice(GpioDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(SpiDevice, self).__init__(deviceName_,rpiScratchIO_,connections_)
    if len(self.connections) != 1:
      raise Exception("ERROR: SPI device %s must have one connection to SPI0 or SPI1" % self.deviceName)
    if self.connections[0] == "SPI0":
      spiDevice = 0
    elif self.connection[0] == "SPI1":
      spiDevice = 1
    else:
      raise Exception("ERROR: SPI device %s must have one connection to SPI0 or SPI1" % self.deviceName)
      
    spiChannel = 0

    # Create a SPI connection
    self.spi = spidev.SpiDev() 
    self.spi.open(spiChannel,spiDevice)

  #-----------------------------

  def cleanup(self):
    self.spi.close()

#=====================================

class FileConnection(GenericDevice):

  def __init__(self,deviceName_,rpiScratchIO_,connections_):
    super(FileConnection, self).__init__(deviceName_,rpiScratchIO_,connections_)
    self.inputChannels += [0] # One channel per file
    self.addSensors() # Add to Scratch

  #-----------------------------

  def config(self,options):
    if self.configured:
      return None
    self.file = open(self.connections[0], options)
    if options.find("w"):
      self.writeMode = True
      self.readMode = False
    if options.find("r+"):
      self.writeMode = True
      self.readMode = True
    else:
      self.writeMode = False
      self.readMode = True
    self.configured = True

  #-----------------------------  

  def read(self,channelId):
    if not self.configured: # Use default read option
      self.config('r')
    if not self.readMode:
      print("WARNING: file %s is open for output only." % self.connections[0])
      return None
    print("WARNING: not currently implemented.")

  #-----------------------------

  def write(self,channelId,value):
    if not self.configured: # Use default write option
      self.config('w')
    if not self.writeMode:
      print("WARNING: file %s is open for input only." % self.connections[0]) 
      return None
    self.file.write(value+"\n")

  #-----------------------------

  def cleanup(self):
    if self.configured:
      self.file.close()

#=====================================
