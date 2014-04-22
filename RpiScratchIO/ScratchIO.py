import os.path, string
import ConfigParser
import RPi.GPIO as GPIO
from ScratchHandler import ScratchHandler
from ConnectionsMgr import ConnectionsMgr

from Devices import *
from SpiDevices import *
#from UsbDevices import *

class ScratchIO:
  __instanceCounter = 0

  def __init__(self,configFile="None"):

    # Use a default configuration name, if none is provided
    if configFile == "None":
      configFile = "RpiScratchIO.cfg"

    # Prevent more than one instance of this class from being created
    if ScratchIO.__instanceCounter > 0:
      raise Exception("Error: can only create one instance of RpiScratchIO")
    ScratchIO.__instanceCounter = 1

    # Check if the configuration file exists
    if not os.path.isfile(configFile):
      raise Exception("Error: configuration file %s not found" % configFile)

    # Read the configuration file
    self.config = ConfigParser.RawConfigParser()
    self.config.optionxform = str # case sensitive keys
    self.config.read(configFile)

    # Create a ConnectionsMgr object, to check the configuration file
    self.connectionsMgr = ConnectionsMgr()

    # Connect to Scratch
    self.scratchHandler = ScratchHandler(self)

    # Create an empty devices dict to store the device objects
    self.devices = {}

    # Parse the input configuration file
    self.__parseConfiguration()

    # This is for debugging
    print(" >> Printing the device connections:")
    self.connectionsMgr.printConnections()

    # Start the Scratch listening thread
    self.scratchHandler.listen()

  #----------------------------------------------

  def __parseConfiguration(self):

    if not self.config.has_section("DeviceTypes"):  # This section must exist!!!
      raise Exception("ERROR: %s contains no device definitions" % configFile)

    # Convert list of pairs to dict and append
    #print self.config.items("DeviceTypes")
    deviceTypes = {}
    deviceConnections = {}
    for device, className in self.config.items("DeviceTypes"):
      #print device
      #print className
      if device in deviceTypes.keys():
        raise Exception("ERROR: %s has already been defined in %s" % (device % configFile))

      if len(className) > 0:
        if not ("(" in className and ")" in className):
          raise Exception("ERROR: class name %s must be followed by parentheses ()" % className)
        deviceTypes[device] = className
      elif "GPIO" in device:
        # Allow BCM numbered GPIO reference without connection listing
        deviceTypes[device] = "SimpleGpio()"
        deviceConnections[device] = [device]
      else:
        # This is not allowed
        raise Exception("ERROR: %s must be assigned a class name" % device)

    # This is optional and not needed if all of the DeviceType
    # declarations are BCM ids
    if self.config.has_section("DeviceConnections"):
      #print self.config.items("DeviceConnections")
      for device, connections in self.config.items("DeviceConnections"):
        #print device
        #print connections
        connections.replace(' ','') # Remove any spaces
        connections.replace('\t','') # Remove any tab characters
        deviceConnections[device] = string.split(connections,',')

    # Now check if all of the devices have connections.
    for device in deviceTypes.keys():
      if not device in deviceConnections.keys():
        #print device
        #print deviceConnections.keys()
        raise Exception("ERROR: device %s has no connections listed" % device)

    # Set GPIO mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Now create each device object and add them to the devices dict.
    for device in deviceTypes.keys():

      # Build the basic arguments string
      basicArguments = "'%s',self,%s" % (device,deviceConnections[device])

      # Look for the last bracket
      objStr = deviceTypes[device]
      #print objStr   
 
      parPos = str.rfind(objStr,"(")
      parPosClose = str.rfind(objStr,")")
      if parPos == -1 or parPosClose <= parPos:
        raise Exception("ERROR: %s must create a class, e.g. MCP3008()" % deviceTypes[device])

      # Prepend the basic arguments, in front of any optional arguments
      # that are given to the class constructor
      newStr = objStr[0:parPos+1] + basicArguments 
      if (parPos - parPosClose) == 1:
        newStr += objStr[parPos+1:]
      else:
        optionalArguments = objStr[parPos+1:parPosClose]
        # If it is just white space
        if optionalArguments.isspace():
          newStr += objStr[parPos+1:]
        else:
          newStr += "," + objStr[parPos+1:]

      objStr = newStr
  

      #print objStr
 
      # Find the semi-colon before the class instantiation
      semiColonPos = str.rfind(objStr,";",0,parPos)

      # Add the name of the object in front of the class constructor call
      if semiColonPos == -1:
        objStr = "deviceObj = " + objStr
      else:
        objStr = objStr[0:semiColonPos+1] + " deviceObj = " + objStr[semiColonPos+1:]

      #print objStr

      exec "%s" % objStr
      deviceObj.addSensors() # Tell Scratch about the input channels
      self.devices[device] = deviceObj


  #----------------------------------------------

  # Since Python does not always call the destructor
  def cleanup(self):
    self.scratchHandler.cleanup()
    for device in self.devices.keys():
      self.devices[device].cleanup()

  #----------------------------------------------
  def __del__(self):
    ScratchIO.__instanceCounter = 0
