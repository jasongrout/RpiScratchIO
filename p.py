import string

msgs = []
msgs += ['READ:GPIO:23']
msgs += ['WRITE:GPIO:23:1']
msgs += ['CONFIG:SPI0:ADC222']
msgs += ['CONFIG:UART0:BRICKPI']
msgs += ['READ:SPI0:ADC222:0']
msgs += ['CONFIG:I2C0:IIC']
msgs += ['TURNIP']
msgs += ['CONFIG:TOSH']

cmds = ['READ','WRITE','CONFIG']
buses = ['GPIO','SPI0','SPI1','UART0','I2C0']

def parseGpioCmd(args):
  bcmId = int(args[2])
  if args[0] == 'READ':
    value = read(bcmId)
    # Now have to send this back to Scratch
  elif args[0] == 'CONFIG':
    if len(args) < 4:
      print "ERROR: to few arguments for GPIO write"
      return
    value = write(bcmId,int(args[3]))

def parseBusCmd(args):
  print args

for msg in msgs:
  if not ':' in msg:
    print "ERROR: badly formatted string"
    continue # should return an error

  frags = string.split(msg,':')
  if len(frags) < 3:
    print "ERROR: not enough arguments"
    continue # should return an error

  if not frags[0] in cmds:
    print "ERROR: %s is not in the list of commands" % frags[0]
    continue # should return an error

  if not frags[1] in buses:
    print "ERROR: %s is not in the list of buses" % frags[1]
    continue # should return an error

  if frags[1] == 'GPIO':
    parseGpioCmd(frags)
  else:
    parseBusCmd(frags)

  print frags
