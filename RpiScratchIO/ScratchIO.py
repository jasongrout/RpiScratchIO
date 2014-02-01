import os.path, string
import ConfigParser
import RPi.GPIO as GPIO
from ScratchHandler import ScratchHandler
from RpiGpioConnections import RpiGpioConnections
from Devices import *

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

    # Create a RpiGpioConnections object, to check the configuration file
    self.rpiGpioConnections = RpiGpioConnections()

    # Connect to Scratch
    self.scratchHandler = ScratchHandler(self)

    # Create an empty devices dict to store the device objects
    self.devices = {}

    # Parse the input configuration file
    self.__parseConfiguration()

    # This is for debugging
    print " >> Printing the device connections:"
    self.rpiGpioConnections.printConnections()

    # Start the Scratch listening thread
    self.scratchHandler.listen()

  #----------------------------------------------

  def __parseConfiguration(self):

    if not self.config.has_section("DeviceTypes"):  # This section must exist!!!
      raise Exception("Error: %s contains no device definitions" % configFile)

    # Convert list of pairs to dict and append
    print self.config.items("DeviceTypes")
    deviceTypes = {}
    deviceConnections = {}
    for device, className in self.config.items("DeviceTypes"):
      print device
      print className
      if device in deviceTypes.keys():
        raise Exception("Error: %s has already been defined in %s" % (device % configFile))

      if len(className) > 0:
        if not ("(" in className and ")" in className):
          raise Exception("Error: class name %s must be followed by parentheses ()" % className)
        deviceTypes[device] = className
      elif "GPIO" in device:
        # Allow BCM numbered GPIO reference without connection listing
        deviceTypes[device] = "SimpleGpio()"
        deviceConnections[device] = [device]
      else:
        # This is not allowed
        raise Exception("Error: %s must be assigned a class name" % device)

    # This is optional and not needed if all of the DeviceType
    # declarations are BCM ids
    if self.config.has_section("DeviceConnections"):
      print self.config.items("DeviceConnections")
      for device, connections in self.config.items("DeviceConnections"):
        print device
        print connections
        connections.replace(' ','') # Remove any spaces
        connections.replace('\t','') # Remove any tab characters
        deviceConnections[device] = string.split(connections,',')

    # Now check if all of the devices have connections.
    for device in deviceTypes.keys():
      if not device in deviceConnections.keys():
        print device
        print deviceConnections.keys()
        raise Exception("Error: device %s has no connections listed" % device)

    # Set GPIO mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Now create each device object and add them to the devices dict.
    for device in deviceTypes.keys():

      # Build the basic arguments string
      basicArguments = "'%s',self,%s" % (device,deviceConnections[device])

      # Prepend the basic arguments, in front of any optional arguments
      objStr = string.replace(deviceTypes[device],"(","("+basicArguments)
      print objStr
      exec "deviceObj = %s" % objStr
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