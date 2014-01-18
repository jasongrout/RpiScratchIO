import scratch

class ScratchHandler:
  def __init__(self, config, gpioSvc):
    self.__gpioSvc = gpioSvc

    # Set the defaults for the connection
    host = "localhost"
    port = 40000

    # If the connection setting are given in the configuration file,
    # then update them.
    if config.has_section("ScratchConnection"):
      host = config.get("ScratchConnection","host")
      port = config.getint("ScratchConnection","port")

    # Read the aliases from the configuration file
    self.__aliases = {}
    if config.has_section("Aliases"):
      # Convert list of pairs to dict and append
      self.__aliases = dict(config.items("Aliases"))

    # Open a Scratch connection.
    #self.scratch = scratch.Scratch(host, port) 
    self.scratchConnection = scratch.Scratch()

    # Give the gpioSvc object a pointer to this object
    gpioSvc.scratchHandler(self)

    # Load the current Scratch session with the GPIO pins and bus
    # devices that are declared within the configuration file.
    gpioSvc.addScratchSensors()


  def __del__(self):
    # Close the Scratch connection.
    self.scratchConnection.disconnect()




  def listen(self):
    while True:
        try:
           yield self.scratchConnection.receive()
        except scratch.ScratchError:
           raise StopIteration

