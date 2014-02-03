import string, sys, threading
import scratch

class ScratchHandler:

  #-----------------------------------------

  def __init__(self, rpiScratchIO_):
    self.__rpiScratchIO = rpiScratchIO_

    # Functions that can be parsed
    self.availableFunctions = ['config','read','write']

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
      print "ERROR: Cannot connect to Scratch."
      print "       Start Scratch with remote sensors enabled before running this program."
      sys.exit(1)

  #-----------------------------------------

  def cleanup(self):
    print " >> Shutting down the connection to Scratch."
    self.shutdown_flag = False
    self.scratchConnection.disconnect()

  #-----------------------------------------

  def clientThread(self):
    self.deviceNames = self.__rpiScratchIO.devices.keys()
    while not self.shutdown_flag:
      try:
        msg = self.scratchConnection.receive()
        if msg[0] == 'broadcast':
          self.__parseBroadcast(msg[1])
        elif msg[0] == 'sensor-update':
          self.__parseSensorUpdate(msg[1])
        else:
          continue
      except scratch.ScratchError:
        self.shutdown_flag = True

  #-----------------------------------------

  def listen(self):
    print " >> Listening for commands from Scratch."
    self.shutdown_flag = False
    self.server_thread = threading.Thread(target=self.clientThread)
    self.server_thread.start()

  #-----------------------------------------

  def __parseBroadcast(self,cmd):
    if not ":" in cmd:
      return None

    frags = string.split(cmd,':',3)
    
    # If the command is not formulated correctly, ignore it.
    # Commands must be: "deviceName:functionName:args"
    # Allow GPIO23:READ without arguments
    if len(frags) != 2 and len(frags) != 3:
      return None

    deviceName = frags[0]
    functionName = frags[1]
    hasArguments = False
    if len(frags) == 3:
      arguments = frags[2]
      hasArguments = True
    else:
      arguments = "None"

    # The device must be available.
    # (Ignore this without a warning message, since it might be a broadcast for another client.)
    if not deviceName in self.deviceNames:
      return None

    # The function must be available
    if not functionName in self.availableFunctions:
      print("WARNING: function name \"%s\" not available.  Available function names:" % functionName)
      for availableFunction in self.availableFunctions:
        print("         %s" % availableFunction)
      return None

    # Split the arguments into a list
    if hasArguments:
      if not ',' in arguments:
        argList = [ arguments ]
      else:
        argList = string.split(arguments,',')
    else:
      argList = []
    nargs = len(argList)

    # Now call the appropriate function
    if functionName == 'read':
      if nargs == 0:
        self.__rpiScratchIO.devices[deviceName].read()
      elif nargs == 1:
        self.__rpiScratchIO.devices[deviceName].read(argList[0])
      else:
        print("WARNING: \"read\" expects zero or one arguments.  %d arguments were given" % nargs)
        return None

    elif functionName == 'write':
      if nargs == 0:
        print("WARNING: \"write\" expects one or two arguments.  No arguments were given")
        return None
      elif nargs == 1:
        # Assume channel zero should be used
        #print deviceName
        #print self.__rpiScratchIO.devices[deviceName]
        #print argList
        self.__rpiScratchIO.devices[deviceName].write("0",argList[0])
      elif nargs == 2:
        self.__rpiScratchIO.devices[deviceName].write(argList[0],argList[1])
      else:
        print("WARNING: \"write\" expects one or two arguments.  %d arguments were given" % nargs)
        return None

    elif functionName == 'config':
      if nargs == 0:
        print("WARNING: \"config\" expects at least one argument.  No arguments were given")
        return None
      else:
        self.__rpiScratchIO.devices[deviceName].config(argList)

  #-----------------------------------------

  def __parseSensorUpdate(self,cmd):

    # The GPIO bcm pins are special and correspond to one channel only.
    # Other devices with one channel, should be allowed to assume channel 0.
    if not ":" in cmd:
      deviceName = cmd
      channelId = "0"
    else:
      frags = string.split(cmd,":")
      deviceName = frags[0]
      channelId = frags[1]

    for deviceName in cmd.keys():
      # Could be some other global variable.
      # Therefore, should not throw an error, but just ignore the change.
      if not deviceName in self.deviceNames:
        return None
      self.__rpiScratchIO.devices[deviceName].write(channelId,cmd[deviceName])
