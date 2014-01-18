import ConfigParser

config = ConfigParser.RawConfigParser()
config.optionxform = str # case sensitive keys
config.read("devices.cfg")

if config.has_section("SpiDevices"):
  print "Has SPI"
  # Convert list of pairs to dict
  print dict(config.items("SpiDevices"))

if config.has_section("Aliases"):
  print "Has aliases"
  # Convert list of pairs to dict
  print dict(config.items("Aliases"))
