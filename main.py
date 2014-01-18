#!/usr/bin/env python
#
import sys, os.path, ConfigParser
from ScratchHandler import ScratchHandler
from GpioSvc import GpioSvc

if __name__ == "__main__":
  configFile = "devices.cfg"
  if len(sys.argv) > 1:
    configFile = sys.argv[1]

  config = None
  # Check if the file exists
  if os.path.isfile(configFile):

    # Read the configuration file
    config = ConfigParser.RawConfigParser()
    config.optionxform = str # case sensitive keys
    config.read(configFile)

  # Start GPIO Svc, passing configuration object
  g = GpioSvc(config)
  
  # Start scratch handler, passing GpioSvc object
  s = ScratchHandler(config,g)

  # Tell scratch about the current remote sensors
  #s.initialise()

  # Tell scratch to listen for commands from Scratch
  #s.listen()
