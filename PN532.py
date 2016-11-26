#micropython on ESP8266
from machine import Pin, I2C
import time

def connect(sda=4, scl=5):
	sda = Pin(sda)
	scl = Pin(scl)
	i2c = I2C(scl=scl, sda=sda, freq=410000)
	return i2c

def addr(i2c):
	return i2c.scan()

def wait_ack(i2c, pn532_addr):
	while True:
		ack = str(i2c.readfrom(pn532_addr, 12)).replace('\\x',' ').replace("b'",'').strip()
		if ack[0:11] == '01 00 00 ff':
			if ack[0:20] == '01 00 00 ff 00 ff 00':
				return True
			else:
				print('ACK %s not success' %ack)
				return False
		time.sleep(0.2)	
	
def read(i2c,addr,len=30):
	rbytes = i2c.readfrom(addr,len)
	result = str(rbytes).replace('\\x',' ').replace("b'",'').strip()
	if result[0:11] == '01 00 00 ff':
		return rbytes
	else:
		return False

def write(i2c,addr,cmd):
		i2c.writeto(addr, cmd)
		time.sleep(0.1)
		if wait_ack(i2c,addr):
			return True
		else:
			return False

def get_version(i2c,addr):
	cmd_version = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x02\xFE\xD4\x02\x2A')
	try:
		i2c=connect()
	except:
		print('Check i2c line')
		return False
	if write(i2c,36,cmd_version):
		return read(i2c,addr)
	
def config(i2c,addr):
	cmd_config = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x05\xFB\xD4\x14\x01\x02\x01\x14')
	if write(i2c,36,cmd_config):
		return True
	else:
		return False

def wait_card(i2c,addr):
	if not config(i2c,addr):
		return False
	cmd_waitcard = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x04\xFC\xD4\x4A\x01\x00\xE1')
	if write(i2c,36,cmd_waitcard):
		while True:
			result = read(i2c,addr,len=100)
			if result:
				result = (' '.join([str('%02X' % c) for c in result]))
				l = int(result[36:38],0)
				nl = 38+l+l/2
				card_num = int(result[39:int(nl)].replace(' ','').strip(),16)
			time.sleep(0.2)
	else:
		return False
	

