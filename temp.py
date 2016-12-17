import visa

rm = visa.ResourceManager()

myinst = rm.open_resource('TCPIP0::10.80.127.13::inst0::INSTR')

myinst.write('*IDN?')
print('Device ID: ', myinst.read())

myinst.write('*CLS')

myinst.write('*OPC?')
print('Check OPC: ', myinst.read(), 'for', myinst)