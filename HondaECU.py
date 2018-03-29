from __future__ import division
from pylibftdi import Device
from struct import unpack
from tabulate import tabulate
import time
import binascii

class HondaECU(Device):
	
	def __init__(self, *args, **kwargs):
		super(HondaECU, self).__init__(*args, **kwargs)
		self.ftdi_fn.ftdi_set_line_property(8, 1, 0)
		self.baudrate = 10400
		self.flush()

	def __cksum(self, data):
		return -sum(data) % 256

	def send(self, buf, response=True):
		msg = ("".join([chr(b) for b in buf]))
		self.write(msg)
		time.sleep(.01)
		self.read(buf[1]) # READ AND DISCARD CMD ECHO
		if response:
			buf = self.read(2)
			if len(buf) > 0:
				buf += self.read(ord(buf[1])-2)
				return buf
			
	def send_command(self, mtype, data=[], debug=False):
		ml = len(mtype)
		dl = len(data)
		msgsize = 0x02 + ml + dl
		msg = mtype + [msgsize] + data
		msg += [self.__cksum(msg)]
		assert(msg[ml] == len(msg))
		if debug: print("->", ["%02x" % m for m in msg])
		resp = self.send(msg)
		if resp:
			assert(ord(resp[-1]) == self.__cksum([ord(r) for r in resp[:-1]]))
			if debug: print("<-", [binascii.hexlify(r) for r in resp])
			rmtype = resp[:ml]
			rml = resp[ml:(ml+1)]
			rdata = resp[(ml+1):-1]
			return (rmtype, rml, rdata)
