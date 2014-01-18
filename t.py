#!/usr/bin/env python
from GpioSvc import *
g = GpioSvc()
print "setOutput=%d" % g.setOutput(23)
print "setInput=%d" % g.setInput(23)
g.release(23)
g.write(23,True)
print "read(23)=%d" % g.read(23)

