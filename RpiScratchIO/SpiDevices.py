from Devices import SpiDevice

#=====================================

# For the chip of the same name
class MCP3008(SpiDevice):

  def __init__(self,deviceName_,scratchIO_,connections_):

    # Call the base class constructor
    super(MCP3008, self).__init__(deviceName_,scratchIO_,connections_)

    # Define the valid input channel numbers
    for i in xrange(8):
      self.inputChannels += [i]

    # Add the input channels as sensors to Scratch
    self.addSensors()

  #-----------------------------

  def read(self,channelId):
    #print "read, channelId = %s" % channelId
    
    # Check if this is a valid input channelId
    channelNumber = self.validInputChannel(channelId)
    if channelNumber == -1:
      return None
    
    # Read data from SPI link
    msg = self.spi.xfer2([1,(8+channelNumber)<<4,0])
    #print "read=%s" % msg

    # Unpack data into ADC counts
    adc_counts = ((msg[1]&3) << 8) + msg[2]

    # Convert ADC counts into voltage
    voltage = round(adc_counts*3.3 / 1023,3)
  
    # Send the value back to Scratch
    self.updateSensor(channelId, voltage)

#=====================================
