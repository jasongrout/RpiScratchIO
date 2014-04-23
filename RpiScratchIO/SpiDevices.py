import spidev
from Devices import GpioDevice

#=====================================

class SpiDevice(GpioDevice):

  def __init__(self,deviceName_,scratchIO_,connections_):
    super(SpiDevice, self).__init__(deviceName_,scratchIO_,connections_)
    if len(self.connections) != 1:
      raise Exception("ERROR: SPI device %s must have one connection to SPI0 or SPI1" % self.deviceName)
    if self.connections[0] == "SPI0":
      spiDevice = 0
    elif self.connections[0] == "SPI1":
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

# For the chip of the same name
class MCP3008(SpiDevice):

  def __init__(self,deviceName_,scratchIO_,connections_):

    # Call the base class constructor
    super(MCP3008, self).__init__(deviceName_,scratchIO_,connections_)

    # Define the valid input channel numbers
    for i in xrange(8):
      self.inputChannels += [i]

  #-----------------------------

  def read(self,channelNumber):
    
    # Read data from SPI link
    msg = self.spi.xfer2([1,(8+channelNumber)<<4,0])

    # Unpack data into ADC counts
    adc_counts = ((msg[1]&3) << 8) + msg[2]

    # Convert ADC counts into voltage
    voltage = round(adc_counts*3.3 / 1023,3)
  
    # Send the value back to Scratch
    self.updateSensor(channelNumber, voltage)

#=====================================
