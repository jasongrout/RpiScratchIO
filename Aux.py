from Devices import *

class MCP4008(SpiDevice):

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
