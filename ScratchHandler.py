import string, sys, threading
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

    # Open a Scratch connection.
    print " >> Connecting to Scratch on %s using port %d" % (host, port)
    try:
      self.scratchConnection = scratch.Scratch(host, port) 
    except scratch.ScratchError:
      print " ERROR: Cannot connect to Scratch."
      print " Start Scratch with remote sensors enabled before running this program."
      sys.exit(1)


  def cleanup(self):
    print "  >> Shutting down the connection to Scratch."
    self.shutdown_flag = False
    self.scratchConnection.disconnect()

  def clientThread(self):
    deviceNames = self.__rpiScratchIO.devices.keys()
    while not self.shutdown_flag:
      try:
        msg = self.scratchConnection.receive()
        if msg[0] == 'broadcast':
          cmd = msg[1]
          frags = string.split(cmd,':')
          
        elif msg[0] == 'sensor-update':
          cmd = msg[1]
          for deviceName in cmd.keys():
            # Could be some other global variable.
            # Therefore, should not throw an error, but just ignore the change.
            if not deviceName in deviceNames:
              continue
            self.__rpiScratchIO.devices[deviceName].write(cmd[deviceName])
        else:
          continue
      except scratch.ScratchError:
        self.shutdown_flag = True
      
  def listen(self):
    print "  >> Listening for commands from Scratch."
    self.shutdown_flag = False
    self.server_thread = threading.Thread(target=self.clientThread)
    self.server_thread.start()
