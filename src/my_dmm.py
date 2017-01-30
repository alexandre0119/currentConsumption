#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import visa
import numpy as np
from pandas import DataFrame, ExcelWriter


# import configparser
# def testtest():
# 	config = configparser.ConfigParser()
# 	config.read('config.ini')
# 	dmm_count = int(str(config['DMM'].get('DMM_count')))
# 	print(dmm_count)
# testtest()


def open_connection(visa_address_list):
	"""
	Open connection for DMM
	:param visa_address_list: Instruments visa address as list
	:return: Instrument list
	"""
	# Open connection
	# rm = visa.ResourceManager('C:\\Program Files (x86)\\IVI Foundation\\VISA\\WinNT\\agvisa\\agbin\\visa32.dll')
	rm = visa.ResourceManager()
	# Loop through instrument visa address list
	inst_list = []
	for i in visa_address_list:
		inst_list.append(rm.open_resource(i))
	return inst_list


def close_connection(inst_list):
	for i in inst_list:
		i.close()


def query_error(inst_list, enable_print):
	"""
	Instrument query error
	:param inst_list: instrument list
	:param enable_print: =1 print message; =others not print message
	:return: error reading list
	"""
	error_reading_list = []
	for i in inst_list:
		i.write('SYST:ERR?')
		error_reading = str(i.read()).strip()
		error_reading_list.append(error_reading)
		if enable_print == 1:
			print('System Error: <{0}> for instrument <{1}>'.format(error_reading, i))
		else:
			pass
	return error_reading_list


def check_opc(inst_list, enable_print):
	"""
	Instrument check OPC
	:param inst_list: instrument list
	:param enable_print: =1 print message; =others not print message
	:return: OPC reading list
	"""
	opc_reading_list = []
	for i in inst_list:
		i.write('*OPC?')
		opc_reading = str(i.read()).strip()
		opc_reading_list.append(opc_reading)
		if enable_print == 1:
			print('Check OPC: <{0}> for instrument <{1}>'.format(opc_reading, i))
		else:
			pass
	return opc_reading_list


def get_idn(inst_list, enable_print):
	"""
	Get instrument ID
	:param inst_list: instrument list
	:param enable_print: =1 print message; =others not print message
	:return: instrument ID
	"""
	idn_reading_list = []
	for i in inst_list:
		i.write('*IDN?')
		idn_reading = str(i.read()).strip()
		idn_reading_list.append(idn_reading)
		if enable_print == 1:
			print('Instrument ID: <{0}> for instrument <{1}>'.format(idn_reading, i))
		else:
			pass
	return idn_reading_list


def text_display(inst_list, text):
	"""
	Display content on instrument
	:param inst_list: instrument list
	:param text: content to display on instrument
	:return:
	"""
	for i in inst_list:
		i.write('DISP:TEXT "{0}"'.format(text))


def dmm_init(inst_list, timeout, current_range,
             trigger_source, trigger_delay,
             sample_source, sample_timer,
             enable_print):
	"""
	Init DMM
	:param inst_list: Instrument list
	:param timeout: DMM max timeout
	:param current_range: DC max range
	:param trigger_source: trigger source: IMM or EXT or BUS
	:param trigger_delay: trigger delay 0 to ~3600 seconds (~20 µs  increment for dc measurements)
	:param sample_source: IMM or TIM
	:param sample_timer: MIN  to ~3600 seconds (~20 µs steps)
	:param enable_print: 1 to enable print
	:return:
	"""
	for i in inst_list:

		i.timeout = timeout  # Set timeout

		i.write('*CLS')  # Clear

		# Config current measurement range and read back
		i.write('CONF:CURR:DC {0}'.format(current_range))
		i.write('CONF?')
		i_curr_range_reading = str(i.read()).strip()
		if enable_print == 1:
			print('Set current range: <{0}> for instrument <{1}>'.format(i_curr_range_reading, i))
		else:
			pass
		# Number of Readings = Sample Count x Trigger Count
		# Trigger SOURce set to IMMediate
		i.write('TRIG:SOUR {0}'.format(trigger_source))  # Immediate (continuous) trigger
		i.write('TRIG:SOUR?')
		i_trig_sour = str(i.read()).strip()
		if enable_print == 1:
			print('Trigger source: <{0} for instrument <{1}>'.format(i_trig_sour, i))
		else:
			pass
		# Trigger delay set to min
		i.write('TRIG:DEL {0}'.format(trigger_delay))
		i.write('TRIG:DEL?')
		i_trig_del = str(i.read()).strip()
		if enable_print == 1:
			print('Trigger delay: <{0}> for instrument <{1}>'.format(i_trig_del, i))
		else:
			pass
		# Sample source to IMM
		i.write('SAMP:SOUR {0}'.format(sample_source))
		i.write('SAMP:SOUR?')
		i_samp_del = str(i.read()).strip()
		if enable_print == 1:
			print('Sample source: <{0}> for instrument <{1}>'.format(i_samp_del, i))
		else:
			pass
		# Sample timer to min
		i.write('SAMP:TIM {0}'.format(sample_timer))
		i.write('SAMP:TIM?')
		i_samp_timer = str(i.read()).strip()
		if enable_print == 1:
			print('Sample timer: <{0}> for instrument <{1}>'.format(i_samp_timer, i))
		else:
			pass

		# i.write('INIT')


def measure_single_dmm(inst, trigger_count, sample_count, enable_print):
	"""
	Get DMM readings and statistics
	:param inst: Instrument list
	:param trigger_count: trigger count
	:param sample_count: sample count
	:param enable_print: enable print out
	:return: raw data list, mean list, max list, min list, std list, count list
	"""
	inst.write('CALC:AVER:CLE')  # Clear statistics
	inst.write('TRIG:COUN {0}'.format(trigger_count))  # Sets the trigger count to X
	inst.write('SAMP:COUN {0}'.format(sample_count))  # Sets X readings per trigger
	inst.write('CALC:STAT ON')  # Turn on Stat calculations for future readings

	inst.write('READ?')  # Get readings

	reading = str(inst.read()).strip().split(',')
	readings = []
	for i_reading in reading:
		readings.append(float(format(float(i_reading) * 1000, 'f')))  # convert unit to mA, default is A

	if enable_print == 1:
		print('Average/Mean: {0:.4f} mA'.format(np.mean(readings)))
		print('Max: {0:.4f} mA'.format(np.max(readings)))
		print('Min: {0:.4f} mA'.format(np.min(readings)))
		print('Sdev: {0:.4f} mA'.format(np.std(readings)))
		print('Total readings: {0}'.format(np.count_nonzero(readings)))
	else:
		pass

	return readings, np.mean(readings), np.max(readings), np.min(readings), np.std(readings), np.count_nonzero(readings)


def dmm_reading_format(reading):
	return [float(format(reading[1], '.4f')),
	        float(format(reading[2], '.4f')),
	        float(format(reading[3], '.4f')),
	        float(format(reading[4], '.4f')),
	        float(format(reading[5], '.0f')),
	        ','.join(map(str, reading[0])), ]


def join_dataframe(case_name, reading):
	data_framed = DataFrame(reading,
	                        index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count', '6.Raw'],
	                        columns=[str(case_name)])
	return data_framed


def dmm_flow_wrapper(visa_address,
                     timeout, current_range, trigger_source, trigger_delay,
                     sample_source, sample_timer,
                     trigger_count, sample_count,
                     case_name, enable_print):
	my_inst_list = open_connection(visa_address)
	# query_error(my_inst_list, enable_print)
	# check_opc(my_inst_list, enable_print)
	# get_idn(my_inst_list, enable_print)
	text_display(my_inst_list, 'Running...')
	dmm_init(my_inst_list, timeout, current_range, trigger_source, trigger_delay,
	         sample_source, sample_timer, enable_print)
	data_frame_list = []
	for i in my_inst_list:
		reading = measure_single_dmm(i, trigger_count, sample_count, enable_print)
		reading_formatted = dmm_reading_format(reading)
		data_frame = join_dataframe(case_name, reading_formatted)
		data_frame_list.append(data_frame)

	print(data_frame_list)

	# Close connection
	text_display(my_inst_list, 'Completed...')
	close_connection(my_inst_list)

	return data_frame_list


def sample_flow():
	"""
	Example test flow
	:return:
	"""
	mylist = ['TCPIP0::192.168.1.11::inst0::INSTR', 'TCPIP0::192.168.1.10::inst0::INSTR']
	# mylist = ['TCPIP0::192.168.1.11::inst0::INSTR']
	myinst_list = open_connection(mylist)
	query_error(myinst_list, 1)
	# check_opc(myinst_list, 1)
	# get_idn(myinst_list, 1)
	# text_display(myinst_list, 'Running...')

	# !!! Seems 34410/34411 MIN sample time is about 35ms, timing violation error show is smaller !!!
	# dmm_init(myinst_list, 600000, 3, 'IMM', 'MIN', 'TIM', 0.0001, 0)
	dmm_init(myinst_list, 600000, 3, 'IMM', 'MIN', 'TIM', 'MIN', 0)

	dmm_reading_list = []
	for i in myinst_list:
		reading = measure_single_dmm(i, 1, 10, 0)
		reading = dmm_reading_format(reading)
		dmm_reading_list.append(reading)
		# print(reading)
		print(join_dataframe('Test', reading))
		print('\n')

	close_connection(myinst_list)


# sample_flow()
