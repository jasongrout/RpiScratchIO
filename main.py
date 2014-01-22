#!/usr/bin/env python
#
import sys
from RpiScratchIO import RpiScratchIO

if __name__ == "__main__":
  configFile = "devices.cfg"
  if len(sys.argv) > 1:
    configFile = sys.argv[1]

  r = RpiScratchIO(configFile)
