import usb.core
from Devices import GenericDevice

#=====================================

# For the chip of the same name
class MaplinArm(GenericDevice):

  def __init__(self,deviceName_,scratchIO_,connections_):

    # Call the base class constructor
    super(MaplinArm, self).__init__(deviceName_,scratchIO_,connections_)

    # Connect to the USB device or throw an exception
    #self.usbDevice = usb.core.find(idVendor=0x1267,idProduct=0x0000)
    #if self.usbDevice is None:
    #  raise Exception("ERROR: Maplin robotic arm not found")

    # Define a dictionary to contain the movements
    # TODO: need to use a bit mask, to allow more than one motion at once.
    self.motorDict = {}
    self.motorDict[0] = {-1:[0,1,0],1:[0,2,0],0:[]} # Base: left, right
    self.motorDict[1] = {-1:[64,0,0],1:[128,0,0],0:[]} # Shoulder : down, up
    self.motorDict[2] = {-1:[16,0,0],1:[32,0,0],0:[]} # Elbow: up, down
    self.motorDict[3] = {-1:[4,0,0],1:[8,0,0],0:[]} # Wrist: up, down
    self.motorDict[4] = {-1:[2,0,0],1:[1,0,0],0:[]} # Grip: open, close
    self.motorDict[5] = {1:[0,0,1],0:[]} # Light: on

    # Store the motor state, to allow masks with
    # respect to the current state
    self.currentMotorCmd = [0,0,0]

    # Define the valid output channel numbers
    for i in xrange(6):
      self.outputChannels += [i]

    # Add the input channels as sensors to Scratch
    #self.addSensors()

  #-----------------------------

  def write(self,channelId,value):

    print "Calling write"

    # Check if this is a valid input channelId
    channelNumber = self.validOutputChannel(channelId)
    if channelNumber == -1:
      return None
    
    # Check if the value is an integer
    try:
      intValue = int(value)
    except ValueError:
      return None
 
    # Catch value errors
    validValues = self.motorDict[channelNumber].keys()
    if not intValue in validValues:
      print("WARNING: the value \"%d\" for channel \"%d\" of device \"%s\" is out of range" % (intValue, channelNumber, self.deviceName))
      print("         Allowed values are: %s" % validValues)

    # If the value is zero, then stop the channel requested
    if intValue == 0:
      self.__setChannelOff(channelNumber)
    else:
      self.__setChannelStatus(channelNumber,intValue)

    # Send the value back to Scratch
    #self.updateSensor(channelId, voltage)

  #-----------------------------
  
  def __setChannelOff(self,channelNumber):
    updateNeeded = False
    
    # Need to stop just this motor channel and
    # allow any other motors or the LED to keep
    # running.  Therefore, use a mask to just
    # turn off affected bits.
    motorChannel = self.motorDict[channelNumber] # Possible settings for this channel
    for intValue in motorChannel.keys(): # Value settings
      settings = motorChannel[intValue] # The list of settings
      for bitIndex in xrange(3): # Positions in the list
        
        # If the bit to set is not in this element of the list,
        # then skip this element of the list
        if settings[bitIndex] == 0:
          continue
        
        # If this bit is not set, skip it 
        if self.currentMotorCmd[bitIndex] & settings[bitIndex] == 0:
          continue
        
        # 8bits all set to 1
        mask = 255
        
        # Turn off just the effected bit
        mask = mask ^ settings[bitIndex]

        print bin(settings[bitIndex])
        print bin(mask)        

        # Now update the current command, with the mask
        self.currentMotorCmd[bitIndex] = self.currentMotorCmd[bitIndex] & mask
        updateNeeded = True
    
    if updateNeeded:
      print "Stopping:"
      print self.currentMotorCmd

  #-----------------------------

  def __setChannelStatus(self,channelNumber,intValue):
    updateNeeded = False

    motorChannel = self.motorDict[channelNumber] # Possible settings for this channel
    settings = motorChannel[intValue] # The list of bits
    for bitIndex in xrange(3): # Positions in the list
        
        # If the bit to set is not in this element of the list,
        # then skip this element of the list
        if settings[bitIndex] == 0: 
          continue
          
        # If this bit is set, skip it
        if self.currentMotorCmd[bitIndex] & settings[bitIndex] == settings[bitIndex]:
          continue

        # Now update the current command, adding the new bit
        # (Other bits are not affected)
        self.currentMotorCmd[bitIndex] = self.currentMotorCmd[bitIndex] | settings[bitIndex]
        updateNeeded = True

    if updateNeeded:
      print "Update:"
      print self.currentMotorCmd

#=====================================
