import scratch

class ScratchHandler:
  def __init__(self, rpiScratchIO_):
    self.__rpiScratchIO = rpiScratchIO_

    # Set the defaults for the connection
    host = "localhost"
    port = 42001
    self.__aliases = {}

    # If the connection setting are given in the configuration file,
    # then update them.
    if self.__rpiScratchIO.config != None:
      if self.__rpiScratchIO.config.has_section("ScratchConnection"):
        host = self.__rpiScratchIO.config.get("ScratchConnection","host")
        port = self.__rpiScratchIO.config.getint("ScratchConnection","port")

      # Read the aliases from the configuration file
      if self.__rpiScratchIO.config.has_section("Aliases"):
        # Convert list of pairs to dict and append
        self.__aliases = dict(self.__rpiScratchIO.config.items("Aliases"))

    # Open a Scratch connection.
    #self.scratch = scratch.Scratch(host, port) 
    #self.scratchConnection = scratch.Scratch()


  def __del__(self):
    # Close the Scratch connection.
    self.scratchConnection.disconnect()


  def listen(self):
    print "listen"

  def stop(self):
    print "stop"

  def listen2(self):
    while True:
        try:
           yield self.scratchConnection.receive()
        except scratch.ScratchError:
           raise StopIteration

