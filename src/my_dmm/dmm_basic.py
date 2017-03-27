#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import visa
import numpy as np
from pandas import DataFrame
# config.ini settings
import src.my_config.config_basic as config_basic
from src.my_misc.my_logging import create_logger
# Logger for DMM
log_dmm = create_logger()


def open_connection_dmm(visa_address_list):
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
	"""
	Close connection
	:param inst_list: instrument list
	:return: None
	"""
	for i in inst_list:
		i.close()


def query_error(inst_list, enable_logging):
	"""
	Instrument query error
	:param inst_list: instrument list
	:param enable_logging: =1 logging message; =others not logging message
	:return: error reading list
	"""
	error_reading_list = []
	for i in inst_list:
		i.write('SYST:ERR?')
		error_reading = str(i.read()).strip()
		error_reading_list.append(error_reading)
		if enable_logging == 1:
			my_str = 'System Error: <{0}> for instrument <{1}>'.format(error_reading, i)
			log_dmm.info(my_str)
		else:
			pass
	return error_reading_list


def check_opc(inst_list, enable_logging):
	"""
	Instrument check OPC
	:param inst_list: instrument list
	:param enable_logging: =1 logging message; =others not logging message
	:return: OPC reading list
	"""
	opc_reading_list = []
	for i in inst_list:
		i.write('*OPC?')
		opc_reading = str(i.read()).strip()
		opc_reading_list.append(opc_reading)
		if enable_logging == 1:
			my_str = 'Check OPC: <{0}> for instrument <{1}>'.format(opc_reading, i)
			log_dmm.info(my_str)
		else:
			pass
	return opc_reading_list


def get_idn(inst_list, enable_logging):
	"""
	Get instrument ID
	:param inst_list: instrument list
	:param enable_logging: =1 logging message; =others not logging message
	:return: instrument ID
	"""
	idn_reading_list = []
	for i in inst_list:
		i.write('*IDN?')
		idn_reading = str(i.read()).strip()
		idn_reading_list.append(idn_reading)
		if enable_logging == 1:
			my_str = 'Instrument ID: <{0}> for instrument <{1}>'.format(idn_reading, i)
			log_dmm.info(my_str)
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
             enable_logging):
	"""
	Init DMM
	:param inst_list: Instrument list
	:param timeout: DMM max timeout
	:param current_range: DC max range
	:param trigger_source: trigger source: IMM or EXT or BUS
	:param trigger_delay: trigger delay 0 to ~3600 seconds (~20 µs  increment for dc measurements)
	:param sample_source: IMM or TIM
	:param sample_timer: MIN  to ~3600 seconds (~20 µs steps)
	:param enable_logging: 1 to enable logging
	:return:
	"""
	for i in inst_list:

		i.timeout = timeout  # Set timeout

		i.write('*CLS')  # Clear

		# Config current measurement range and read back
		i.write('CONF:CURR:DC {0}'.format(current_range))
		i.write('CONF?')
		i_curr_range_reading = str(i.read()).strip()
		if enable_logging == 1:
			my_str = 'Set current range: <{0}> for instrument <{1}>'.format(i_curr_range_reading, i)
			log_dmm.info(my_str)
		else:
			pass
		# Number of Readings = Sample Count x Trigger Count
		# Trigger SOURce set to IMMediate
		i.write('TRIG:SOUR {0}'.format(trigger_source))  # Immediate (continuous) trigger
		i.write('TRIG:SOUR?')
		i_trig_sour = str(i.read()).strip()
		if enable_logging == 1:
			my_str = 'Trigger source: <{0} for instrument <{1}>'.format(i_trig_sour, i)
			log_dmm.info(my_str)
		else:
			pass
		# Trigger delay set to min
		i.write('TRIG:DEL {0}'.format(trigger_delay))
		i.write('TRIG:DEL?')
		i_trig_del = str(i.read()).strip()
		if enable_logging == 1:
			my_str = 'Trigger delay: <{0}> for instrument <{1}>'.format(i_trig_del, i)
			log_dmm.info(my_str)
		else:
			pass
		# Sample source to IMM
		i.write('SAMP:SOUR {0}'.format(sample_source))
		i.write('SAMP:SOUR?')
		i_samp_del = str(i.read()).strip()
		if enable_logging == 1:
			my_str = 'Sample source: <{0}> for instrument <{1}>'.format(i_samp_del, i)
			log_dmm.info(my_str)
		else:
			pass
		# Sample timer to min
		i.write('SAMP:TIM {0}'.format(sample_timer))
		i.write('SAMP:TIM?')
		i_samp_timer = str(i.read()).strip()
		if enable_logging == 1:
			my_str = 'Sample timer: <{0}> for instrument <{1}>'.format(i_samp_timer, i)
			log_dmm.info(my_str)
		else:
			pass

		# i.write('INIT')


def measure_single_dmm(inst, trigger_count, sample_count, enable_logging):
	"""
	Get DMM readings and statistics
	:param inst: Instrument list
	:param trigger_count: trigger count
	:param sample_count: sample count
	:param enable_logging: enable logging
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

	if enable_logging == 1:
		str_avg = 'Average/Mean: {0:.4f} mA'.format(np.mean(readings))
		str_max = 'Max: {0:.4f} mA'.format(np.max(readings))
		str_min = 'Min: {0:.4f} mA'.format(np.min(readings))
		str_sdev = 'Sdev: {0:.4f} mA'.format(np.std(readings))
		str_count = 'Total reading count: {0}'.format(np.count_nonzero(readings))
		log_dmm.info(str_avg)
		log_dmm.info(str_max)
		log_dmm.info(str_min)
		log_dmm.info(str_sdev)
		log_dmm.info(str_count)
	else:
		pass

	return readings, np.mean(readings), np.max(readings), np.min(readings), np.std(readings), np.count_nonzero(readings)


def dmm_reading_format(reading):
	"""
	Format DMM return data
	:param reading: DMM raw data
	:return: formatted DMM data
	"""
	return [float(format(reading[1], '.3f')),
	        float(format(reading[2], '.3f')),
	        float(format(reading[3], '.3f')),
	        float(format(reading[4], '.3f')),
	        float(format(reading[5], '.0f')),
	        ','.join(map(str, reading[0])), ]


def join_dataframe(case_name, reading):
	"""
	Create DataFrame based on DMM readings
	:param case_name: Test case name
	:param reading: DMM readings
	:return: DataFrame
	"""
	data_framed = DataFrame(reading,
	                        index=['1.Average', '2.Max', '3.Min', '4.Sdev', '5.Count', '6.Raw'],
	                        columns=[str(case_name)])
	return data_framed


def dmm_flow_wrapper(visa_address,
                     timeout, current_range, trigger_source, trigger_delay,
                     sample_source, sample_timer,
                     trigger_count, sample_count,
                     case_name, enable_logging):
	"""
	Create DataFrame list based on all active DMM readings
	:param visa_address: Instrument VISA address
	:param timeout: Instrument max timeout (mS)
	:param current_range: current max range (A)
	:param trigger_source: Trigger source
	:param trigger_delay: Trigger delay
	:param sample_source: Sample source
	:param sample_timer: Sample timer
	:param trigger_count: Trigger count
	:param sample_count: Sample count
	:param case_name: test case name
	:param enable_logging: enable logging
	:return: DataFrame list
	"""
	my_inst_list = open_connection_dmm(visa_address)
	# query_error(my_inst_list, enable_logging)
	# check_opc(my_inst_list, enable_logging)
	# get_idn(my_inst_list, enable_logging)
	text_display(my_inst_list, 'Running...')
	dmm_init(my_inst_list, timeout, current_range, trigger_source, trigger_delay,
	         sample_source, sample_timer, enable_logging)
	data_frame_list = []
	for i in my_inst_list:
		reading = measure_single_dmm(i, trigger_count, sample_count, enable_logging)
		reading_formatted = dmm_reading_format(reading)
		data_frame = join_dataframe(case_name, reading_formatted)
		data_frame_list.append(data_frame)

	# log_dmm.info(data_frame_list)

	# Close connection
	text_display(my_inst_list, 'Waiting...')
	close_connection(my_inst_list)

	return data_frame_list


def sample_flow():
	"""
	Sample flow function, only used in this module
	:return: None
	"""
	mylist = ['TCPIP0::192.168.1.11::inst0::INSTR', 'TCPIP0::192.168.1.10::inst0::INSTR']
	# mylist = ['TCPIP0::192.168.1.11::inst0::INSTR']
	myinst_list = open_connection_dmm(mylist)
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
		# log_dmm.info(reading)
		log_dmm.info(join_dataframe('Test', reading))
		log_dmm.info('\n')

	close_connection(myinst_list)

# sample_flow()


def test_case_init_wrapper(case_name, case_count_type, case_func, *args, **kwargs):
	"""
	Set DUT to deep sleep mode and measure. Deep sleep mode is always measured as 1st data
	:param case_name: Test case name
	:param case_count_type: trigger/sample count type 0: flat; 1: pulse; 2: active
	:param case_func: Test case function
	:param args: Test case function args
	:param kwargs: Test case function kwargs
	:return: Measurement results DataFrame list
	"""
	case_count_type = int(case_count_type)
	start_str = '''
	================================================================
	****************************************************************
	>>>> Start measure case [{0}]
	----------------------------------------------------------------
	'''
	end_str = '''
	----------------------------------------------------------------
	Finish measure case [{0}] <<<<
	****************************************************************
	================================================================
	'''
	final_start_str = (start_str.format(case_name))
	final_end_str = (end_str.format(case_name))
	log_dmm.info(final_start_str)
	case_func(*args, **kwargs)
	data_frame_list = dmm_flow_wrapper(config_basic.visa_address_active_list(),
	                                   config_basic.dmm_timeout(),
	                                   config_basic.dmm_current_range(),
	                                   config_basic.dmm_trig_src(),
	                                   config_basic.dmm_trig_delay(),
	                                   config_basic.dmm_sample_src(),
	                                   config_basic.dmm_sample_timer(),
	                                   config_basic.dmm_trigger_count()[case_count_type],
	                                   config_basic.dmm_sample_count()[case_count_type], case_name, 0)
	log_dmm.info(final_end_str)
	return data_frame_list


def test_case_wrapper(case_name, joined_df_list, enable, case_count_type, case_func, *args, **kwargs):
	enable = int(str(enable))
	if enable == 1:
		case_count_type = int(case_count_type)
		start_str = '''
		================================================================
		****************************************************************
		>>>> Start measure [{0}]
		----------------------------------------------------------------
		'''
		end_str = '''
		----------------------------------------------------------------
		Finish measure [{0}] <<<<
		****************************************************************
		================================================================
		'''
		final_start_str = start_str.format(case_name)
		final_end_str = end_str.format(case_name)
		log_dmm.info(final_start_str)
		print('Measuring {0}......'.format(case_name))
		case_func(*args, **kwargs)
		data_frame_list = dmm_flow_wrapper(config_basic.visa_address_active_list(),
		                                   config_basic.dmm_timeout(),
		                                   config_basic.dmm_current_range(),
		                                   config_basic.dmm_trig_src(),
		                                   config_basic.dmm_trig_delay(),
		                                   config_basic.dmm_sample_src(),
		                                   config_basic.dmm_sample_timer(),
		                                   config_basic.dmm_trigger_count()[case_count_type],
		                                   config_basic.dmm_sample_count()[case_count_type], case_name, 0)
		for i in range(len(config_basic.visa_address_active_list())):
			joined_df_list[i] = joined_df_list[i].join(data_frame_list[i])
		log_dmm.info(final_end_str)
		return joined_df_list
	else:
		skip_str = '''
		****************************************************************
		>>>> Skip [{0}]
		****************************************************************
		'''
		final_skip_str = skip_str.format(case_name)
		log_dmm.info(final_skip_str)
		return joined_df_list