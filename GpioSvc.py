import RPi.GPIO as GPIO
from BusDevices import *

#============================================

class GpioPin:
  UNCONFIG = -1
  READ = 0
  WRITE = 1  

  #----------------------------

  def __init__(self,_connectorNumber,_pinNumber,_bcmNumber,_busUsage,_gpioState=-1,_busState=False):
    self.connectorNumber = _connectorNumber
    self.pinNumber = _pinNumber
    self.bcmNumber = _bcmNumber
    self.busUsage = _busUsage # bus type
    self.gpioState = _gpioState # -1 not configured, 0 read, 1 write
    self.busState = _busState # to signal if used for bus
    self.__validGpioStates = [ GpioPin.UNCONFIG, GpioPin.READ, GpioPin.WRITE ]

  #----------------------------

  def setBusState(self, state):
    # The GPIO pins must not be configured
    if self.gpioState != GpioPin.UNCONFIG:
      return 1
    self.busState = state
    return 0

  #----------------------------

  def setGpioState(self, state, pullUpDown):
    # The GPIO pin must to be associated with a bus connection.
    if self.busState: 
      return 1
    # The GPIO state must be a valid state.
    if not state in self.__validGpioStates:
      return 2
    self.gpioState = state

    if state == GpioPin.READ or state == GpioPin.WRITE:
      if state == GpioPin.READ:
        gpioIO = GPIO.IN
      else:
        gpioIO = GPIO.OUT
        
      if pullUpDown != 'None':
        GPIO.setup(self.bcmNumber, gpioIO, pullUpDown)
      else:
        GPIO.setup(self.bcmNumber, gpioIO)      
    return 0

  #----------------------------

  def read(self):
    # If the pin is not enabled as an output pin, try to configure it
    # as an output pin.
    if self.__gpioState != GpioPin.READ:
      ret_val = self.setGpioState(GpioPin.READ,'None')
      if ret_val != 0:
        return -9999*ret_val
    return GPIO.input(self.bcmNumber)

  #----------------------------

  def write(self, state):
    # If the pin is not enabled as an output pin, try to configure it
    # as an output pin.
    if self.__gpioState != GpioPin.WRITE:
      ret_val = self.setGpioState(GpioPin.WRITE,'None')
      if ret_val != 0:
        return ret_val
    if state == 1 or state == 0:
      GPIO.output(self.bcmNumber,state)
      return 0
    return 2

  #----------------------------

#============================================

class GpioSvc:
  def __init__(self,config):
    # List of composite devices or bus devices
    self.__devices = {}

    self.__boardVersion = GPIO.RPI_REVISION
    # NEED to die if boardVersion is not 1 or 2.

    GPIO.setmode(GPIO.BCM)
    self.__gpioPins = {}

    # ---------------------------------------
    # P1 header 
    # pin 1 is 3V3
    # pin 2 is 5V
    # pin 3:
    if self.__boardVersion == 1:
      self.__gpioPins[0] = GpioPin(1,3,0,'I2C0_SDA')
    elif self.__boardVersion == 2:
      self.__gpioPins[2] = GpioPin(1,3,2,'I2C1_SDA')

    # pin 4 is 5V
    # pin 5:
    if self.__boardVersion == 1:
      self.__gpioPins[1] = GpioPin(1,5,1,'I2C0_SCL')
    elif self.__boardVersion == 2:
      self.__gpioPins[3] = GpioPin(1,5,3,'I2C1_SCL')
    # pin 6 is GND
    # pin 7:
    self.__gpioPins[4] = GpioPin(1,7,4,'GPCLK0')
    # pin 8:
    self.__gpioPins[14] = GpioPin(1,8,14,'UART0_TXD')
    # pin 9 is GND
    # pin 10:
    self.__gpioPins[15] = GpioPin(1,10,15,'UART0_RXD')
    # pin 11:
    self.__gpioPins[17] = GpioPin(1,11,17,'None')
    # pin 12:
    self.__gpioPins[18] = GpioPin(1,12,18,'PCM_CLK')
    # pin 13:
    if self.__boardVersion == 1:
      self.__gpioPins[21] = GpioPin(1,13,21,'None')
    elif self.__boardVersion == 2:
      self.__gpioPins[27] = GpioPin(1,13,27,'None')
    # pin 14 is GND
    # pin 15:
    self.__gpioPins[22] = GpioPin(1,15,22,'None')
    # pin 16:
    self.__gpioPins[23] = GpioPin(1,16,23,'None')
    # pin 17 is 3V3
    # pin 18:
    self.__gpioPins[24] = GpioPin(1,18,24,'None')
    # pin 19:
    self.__gpioPins[10] = GpioPin(1,19,10,'SPI0_MOSI')
    # pin 20 is GND
    # pin 21:
    self.__gpioPins[9] = GpioPin(1,21,9,'SPI0_MISO')
    # pin 22:
    self.__gpioPins[25] = GpioPin(1,22,25,'None')
    # pin 23:
    self.__gpioPins[11] = GpioPin(1,23,11,'SPI0_SCLK')
    # pin 24:
    self.__gpioPins[8] = GpioPin(1,24,8,'SPI0_CE0')
    # pin 25 is GND
    # pin 16:
    self.__gpioPins[7] = GpioPin(1,26,7,'SPI0_CE1')
    
    # ---------------------------------------
    if self.__boardVersion == 2:
      # P5 header
      # pin 1 is 5V
      # pin 2 is 3V3
      # pin 3:
      self.__gpioPins[28] = GpioPin(5,3,28,'I2C0_SDA')
      # pin 4:
      self.__gpioPins[29] = GpioPin(5,4,29,'I2C0_SCL')
      # pin 5:
      self.__gpioPins[30] = GpioPin(5,5,30,'None')
      # pin 6:
      self.__gpioPins[31] = GpioPin(5,6,31,'None')
      # pin 7 is GND
      # pin 8 is GND
    

    # Reduce the number of string comparisons once the program is
    # running.
    self.__spi0_pins = []
    self.__i2c0_pins = []
    self.__i2c1_pins = []
    self.__uart0_pins = []
    for bcmId in self.__gpioPins.keys():
      if 'SPI0' in self.__gpioPins[bcmId].busUsage:
        self.__spi0_pins += [bcmId]
      elif 'I2C0' in self.__gpioPins[bcmId].busUsage:
        self.__i2c0_pins += [bcmId]
      elif 'I2C1' in self.__gpioPins[bcmId].busUsage:
        self.__i2c1_pins += [bcmId]
      elif 'UART0' in self.__gpioPins[bcmId].busUsage:
        self.__uart0_pins += [bcmId]

    #print self.spi0_pins
    #print self.i2c0_pins
    #print self.i2c1_pins
    #print self.uart0_pins

    if config != None:
      self.__readConfig(config)


  def __del__(self):
    GPIO.cleanup()

  #-------------------------------------------------

  def __readConfig(self,config):
    if config.has_section("SpiDevices"):

      # Convert list of pairs to dict and append
      spiDevicesConfig = dict(config.items("SpiDevices"))

      # For each bus device, enable the given bus
      # and disable the GPIO pins for other usage
      for spiBus in spiDevicesConfig.keys():
        constructorStr = "spiDev=" + spiDevicesConfig[spiBus]

        if spiBus == "SPI0":
          self.enableSPI0()
          constructorStr += "(0,0)"
          
        elif spiBus == "SPI1":
          self.enableSPI1()
          constructorStr += "(0,1)"

        # Assign object to spiDev
        exec constructorStr

        # Add to dictionary, using the key form 
        # SPI0:NAME that matches the command form
        # used by the ScratchHandler.
        self.__devices[spiBus + ":" + spiDevicesConfig[spiBus]] = spiDev

  #-------------------------------------------------

  def __setBusState(self,bcmList,state):
    for bcmId in bcmList:
      ret_val = self.__gpioPins[bcmId].setBusState(state)
      return ret_val
    return 0

  def enableSPI0(self):
    self.__setBusState(self.__spi0_pins,True)
    return 0

  def releaseSPIO(self):
    self.__setBusState(self.__spi0_pins,False)
    return 0

  def enableI2C0(self):
    self.__setBusState(self.__i2c0_pins,True)
    return 0

  def releaseI2CO(self):
    self.__setBusState(self.__i2c0_pins,False)
    return 0

  def enableI2C1(self):
    if self.__boardVersion == 1:
      #print("ERROR: I2C1 is not available on this type of Raspberry Pi.") 
      return 1
    else:
      self.__setBusState(self.__i2c1_pins,True)
      return 0

  def releaseI2C1(self):
    if self.__boardVersion == 1:
      #print("ERROR: I2C1 is not available on this type of Raspberry Pi.") 
      return 1
    else:
      self.__setBusState(self.__i2c1_pins,False)
      return 0

  def enableUART0(self):
    self.__setBusState(self.__uart0_pins,True)
    return 0

  def releaseUART0(self):
    self.__setBusState(self.__uart0_pins,False)
    return 0

  def readDevice(self,deviceRef,channel):
    # todo. return error if no such device.
    return self.__devices[deviceRef].read(channel)

  def writeDevice(self,deviceRef,channel,signal):
    # todo. return error if no such device.
    self.__devices[deviceRef].write(channel,signal)
    

  #-------------------------------------------------

  def setGpioInput(self,bcmId,pullUpDown='None'):
    return self.__gpioPins[bcmId].setGpioState(GpioPin.READ,pullUpDown)

  def setGpioOutput(self,bcmId):
    return self.__gpioPins[bcmId].setGpioState(GpioPin.WRITE,'None')

  def releaseGpio(self,bcmId):
    return self.__gpioPins[bcmId].setGpioState(GpioPin.UNCONFIG,'None')
    
  def writeGpio(self,bcmId,signal):
    return self.__gpioPins[bcmId].write(signal)
  
  def readGpio(self,bcmId):
    return self.__gpioPins[bcmId].read()

  #-------------------------------------------------

  def scratchHandler(self,s):
    self.__scratchHandler = s

  def addScratchSensors(self):
    # Build a dictionary of all available sensors
    sensorDict = {}

    # If a GPIO pin is not allocated to a bus, add it to the list of
    # sensors.
    for bcmId in self.__gpioPins.keys():
      if not self.__gpioPins[bcmId].busState:
        sensorDict["GPIO:" + str(bcmId)] = 0
  
    # Loop over all of the attached bus devices and add any input
    # channels as sensors
    for deviceKey in self.__devices.keys():
      prefix = deviceKey + ":"
      for channel in self.__devices[deviceKey].inputChannels():
        sensorDict[prefix + str(channel)] = 0

    self.__scratchHandler.scratchConnection.sensorupdate(sensorDict)
  
