import string
import RPi.GPIO as GPIO

#============================================

class GpioPin:

  def __init__(self,_connectorNumber,_pinNumber,_bcmNumber,_busUsage):
    self.connectorNumber = _connectorNumber
    self.pinNumber = _pinNumber
    self.bcmNumber = _bcmNumber
    self.busUsage = _busUsage # bus type
    self.associatedDevices = []

#============================================

class ConnectionsMgr:

  def __init__(self):

    # Dictionary of device names and their associated connections.
    #self.__spi0_devices = {}

    # Get the board version since 
    self.__boardVersion = GPIO.RPI_REVISION
    if self.__boardVersion != 1 and self.__boardVersion != 2:
      raise NotImplementedException(" ERROR: expect board version 1 or 2")

    # Fill the GPIO pin dictionary with the pin mapping.
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
    self.__spi1_pins = []
    self.__i2c0_pins = []
    self.__i2c1_pins = []
    self.__uart0_pins = []
    for bcmId in self.__gpioPins.keys():
      if 'SPI0' in self.__gpioPins[bcmId].busUsage:
        if not 'SPI0_CE1' in self.__gpioPins[bcmId].busUsage:
          self.__spi0_pins += [bcmId]
        if not 'SPI0_CE0' in self.__gpioPins[bcmId].busUsage:
          self.__spi1_pins += [bcmId]
      
      elif 'I2C0' in self.__gpioPins[bcmId].busUsage:
        self.__i2c0_pins += [bcmId]
      elif 'I2C1' in self.__gpioPins[bcmId].busUsage:
        self.__i2c1_pins += [bcmId]
      elif 'UART0' in self.__gpioPins[bcmId].busUsage:
        self.__uart0_pins += [bcmId]

    self.__spi0_devices = []
    self.__spi1_devices = []
    self.__i2c0_devices = []
    self.__i2c1_devices = []
    self.__uart0_devices = []
    self.__usb_devices = []

  #-------------------------------------------------

  def requestGpioIds(self,deviceName,connections):
    for connection in connections:

      # If this is a GPIO connection
      if connection.find("GPIO") == 0:
        bcmId = int(string.replace(connection,'GPIO',''))
        if not bcmId in self.__gpioPins.keys():
          raise Exception("ERROR: unknown BCM id %d" % bcmId)
        if len(self.__gpioPins[bcmId].associatedDevices) != 0:
          raise Exception("ERROR: cannot associate %s with BCM id %d, since this BCM id is already taken")
        self.__gpioPins[bcmId].associatedDevices += [ deviceName ]

      elif connection.find("SPI") == 0:
        if connection == "SPI0":
          if len(self.__spi0_devices) != 0:
            raise Exception("ERROR: %s is already allocated SPI0.0" % self.__spi0_devices)
          self.__spi0_devices += [deviceName]
          for bcmId in self.__spi0_pins:
            self.__gpioPins[bcmId].associatedDevices += [ deviceName ]
        elif connection == "SPI1":
          if len(self.__spi1_devices) != 0:
            raise Exception("ERROR: %s is already allocated SPI0.1" % self.__spi1_devices)
          self.__spi1_devices += [deviceName]
          for bcmId in self.__spi1_pins:
            self.__gpioPins[bcmId].associatedDevices += [ deviceName ]
        else:
          raise Exception("ERROR: unknown connection type %s")

      elif connection.find("I2C") == 0:
        if connection == "I2C0":
          for bcmId in self.__i2c0_pins:
            self.__gpioPins[bcmId].associatedDevices += [ deviceName ]
        elif connection == "I2C1":
           if self.__boardVersion != 2:
             raise Exception("ERROR: error I2C1 is not available on this board type.")
           for bcmId in self.__i2c1_pins:
             self.__gpioPins[bcmId].associatedDevices += [ deviceName ]
        else:
          raise Exception("ERROR: unknown connection type %s")
      elif connection.find("UART0") == 0:
        if len(self.__uart0_devices) != 0:
          raise Exception("ERROR: %s is already allocated UART0" % self.__spi0_devices)
        self.__uart0_devices += [deviceName]
        for bcmId in self.__uart0_pins:
          self.__gpioPins[bcmId].associatedDevices += [ deviceName ]
      else:
        raise Exception("ERROR: unknown connection type %s")


  #-------------------------------------------------
  def printConnections(self):
    for bcmId in self.__gpioPins.keys():
      if len(self.__gpioPins[bcmId].associatedDevices) > 0 :
        print "BCM id %d, connector P%d, pin number %d, attached devices %s" % (bcmId, self.__gpioPins[bcmId].connectorNumber, self.__gpioPins[bcmId].pinNumber, self.__gpioPins[bcmId].associatedDevices)
    if len(self.__spi0_devices) > 0:
      print "SPIO_0 devices = %s" % self.__spi0_devices
    if len(self.__spi1_devices) > 0:
      print "SPIO_1 devices = %s" % self.__spi1_devices
    if len(self.__i2c0_devices) > 0:
      print "I2C0 devices = %s" % self.__i2c0_devices
    if len(self.__i2c1_devices) > 0:
      print "I2C1 devices = %s" % self.__i2c1_devices
    if len(self.__uart0_devices) > 0:
      print "UART0 devices = %s" % self.__uart0_devices
    if len(self.__usb_devices) > 0:
      print "USB devices = %s" % self.__usb_devices
