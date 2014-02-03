============
RpiScratchIO
============

RpiScratchIO is a package that provides additional IO functionality to 
Scratch, running on a local Raspberry Pi or on a remote Raspberry Pi or 
other computer.  The package uses the scratchpy client interface to connect 
to a Scratch server process.  The package can be used by running the 
RpiScratchIO script or via::

    #!/usr/bin/env python

    import time
    import RpiScratchIO
    from RpiScratchIO import ScratchIO
    s = ScratchIO.ScratchIO("myConfig.cfg")
    try:
      while 1:
        time.sleep(1000)

    except KeyboardInterrupt:
      s.cleanup()


Configuration file
==================

The configuration file is read using ConfigParser.  The file has three 
sections, e.g.::

    # Unique device name and class.  If the device name is a GPIO
    # BCM id, then no class name is needed.
    [DeviceTypes]
    GPIO23 =
    ADC = MCP3008()
    Motor = HBRIDGE()
    file = FileConnection()

    # The connection mapping for each device.  Simple GPIO devices do
    # not need a mapping.  The unique device name must be defined in 
    # the DeviceTypes section before the DeviceConnections section.
    [DeviceConnections]
    ADC = SPI0
    MOTOR = GPIO12,GPIO13,GPIO02
    file = file.txt

    # Used to connect to the Scratch server.  Set the host name to
    # localhost to use the local Scratch server or choose an IP of
    # another Scratch server.
    [ScratchConnection]
    host = localhost
    port = 42001

DeviceTypes
-----------

* The name used before the equals sign must be unique.  It is the name
  that Scratch will use to refer to the device.

* The text to the right of the equals sign should correspond to a class
  instantiation.  The string is interpreted as Python, where the default
  arguments are passed to the class constructor.  This means that
  Additional arguments can be included inside the constructor call and
  import statements can be used to include other Python classes.

* In the case of a device name that is a GPIO BCM number (e.g. GPIO23),
  no object needs to be assigned since a SimpleGpio object is assgined
  by default.

DeviceConnections
-----------------

* The DeviceConnections section must be after the DeviceTypes section.

* The device connections define the physical wiring of the components
  or the connection between file names within Scratch and physicial
  file names on disk.

* The device name on the left of the equals sign must be declared in the
  DeviceTypes before it is used here.

* The text to the right of the equals can be a single BCM pin reference,
  a list of BCM pin references separated by commas or buses.  Valid bus
  names are I2C0, I2C1, SPI0, SPI1, UART0.

Starting Scratch
================

* Scratch must be started before the ScratchIO object is instantiated.

* Remote sensors must be enabled by selecting the **Sensors** tool palette.
  Then right click on **sensor value**. Then select 
  *enable remote sensor connections*.

