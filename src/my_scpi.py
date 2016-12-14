#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

# import python modules
import visa
import time
import sys
import threading
import numpy as np
from pyvisa import util
import logging
from src.my_logging import *
import configparser
from src.my_ssh import *
from pandas import DataFrame, ExcelWriter
import queue

config = configparser.ConfigParser()
config.read('config.ini')

visa.logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('(%(threadName)-10s) %(message)s',)
ch.setFormatter(formatter)
visa.logger.addHandler(ch)

active_queues = []
class ThreadWithReturnValue(threading.Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
		threading.Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
		self.mailbox = queue.Queue()
		active_queues.append(self.mailbox)
		self._return = None

	def run(self):
		# logger_append.info('running')
		if self._target is not None:
			self._return = self._target(*self._args, **self._kwargs)
		# return

	def join(self):
		threading.Thread.join(self)
		return self._return

# Define Functions for Binary Data Management

def binblock_raw(data_in):
	# This function interprets the header for a definite binary block
	# and returns the raw binary data for both definite and indefinite binary blocks

	startpos = data_in.find("#")
	if startpos < 0:
		raise IOError("No start of block found")
	lenlen = int(data_in[startpos + 1:startpos + 2])  # get the data length length

	# If it's a definite length binary block
	if lenlen > 0:
		# Get the length from the header
		offset = startpos + 2 + lenlen
		datalen = int(data_in[startpos + 2:startpos + 2 + lenlen])
	else:
		# If it's an indefinite length binary block get the length from the transfer itself
		offset = startpos + 2
		datalen = len(data_in) - offset - 1

	# Extract the data out into a list.
	return data_in[offset:offset + datalen]


def queryError(myinst_list):
	for i in myinst_list:
		i.write('SYST:ERR?')
		print('System Error:', i.read())
		i.write('STAT:QUES?')
		print('Questionable Data Register:', i.read())


def checkOPC(myinst_list):
	for i in myinst_list:
		i.write('*OPC?')
		print('Check OPC: ', i.read(), 'for', i)


def dmmInit(myinst_list):
	for i in myinst_list:
		i.write('DISP:TEXT "Running..."')
		# Set Timeout
		i.timeout = int(config['DMM'].get('DMM_timeout'))

		# *IDN? - Query Instrumnet ID
		i.write('*CLS')  # Clear first
		i.write('*IDN?')  # Get the device ID
		# util.get_debug_info()
		print('Device ID: ', i.read())
		checkOPC(myinst_list)

		# Config current measurement range to 3A and read back
		i.write('CONF:CURR:DC 3')
		i.write('CONF?')
		print('Current Config: ', i.read())
		checkOPC(myinst_list)

		# Number of Readings = Sample Count x Trigger Count
		i.write('TRIG:SOUR IMM')  # Immediate (continuous) trigger
		i.write('TRIG:SOUR?')
		print('Trigger Source:', i.read())
		# i.write('TRIG:DEL:AUTO ON')
		# i.write('TRIG:DEL:AUTO?')
		# print('Trigger Delay:', i.read())
		i.write('TRIG:DEL MIN')
		i.write('TRIG:DEL?')
		print('Trigger Delay:', i.read())
		i.write('SAMP:SOUR IMM')
		i.write('SAMP:SOUR?')
		print('Sample Source:', i.read())
		i.write('SAMP:TIM MIN')
		i.write('SAMP:TIM?')
		print('Sample Timer:', i.read())


def resultFormat(result):
	return [float(format(result[1], '.4f')),
			float(format(result[2], '.4f')),
			float(format(result[3], '.4f')),
			float(format(result[4], '.4f')),
			float(format(result[5], '.0f'))]


def captureOnce(trigger_count, sample_count, myinst):
	myinst.write('TRIG:COUN {0}'.format(trigger_count))  # Sets the trigger count to X
	myinst.write('SAMP:COUN {0}'.format(sample_count))  # Sets X readings per trigger, above 284 sample will be error
	print(myinst)
	# checkOPC(myinst_list)

	# Clear all calculations before we start
	myinst.write('CALC:AVER:CLE')
	print('Statistic cleared\n')

	# Turn on Stat calculations for future readings
	myinst.write('CALC:STAT ON')
	myinst.write('CALC:STAT?')
	print('Calc Enable/Disable:', myinst.read())

	# Get the readings
	myinst.write('READ?')
	# myinst.write('INIT')
	# myinst.write('FETC?')
	reading = str(myinst.read()).strip().split(',')
	readings = []
	for i in reading:
		readings.append(float(format(float(i) * 1000, 'f')))

	# for j in readings:
	# 	# print(type(j))
	# 	print(j, ' mA')
	# print(np.mean(readings))

	# Get average from the readings
	# myinst.write('CALC:AVER:AVER?')
	# reading_avg = format(float(str(myinst.read()).strip()) * 1000, 'f')
	# print('Average/Mean:', reading_avg, ' mA')
	print('Average/Mean: {0:.4f} mA'.format(np.mean(readings)))

	# Get maximum from the readings
	# myinst.write('CALC:AVER:MAX?')
	# reading_max = format(float(str(myinst.read()).strip()) * 1000, 'f')
	# print('Max: ', reading_max, ' mA')
	print('Max: {0:.4f} mA'.format(np.max(readings)))

	# Get minimum from the readings
	# myinst.write('CALC:AVER:MIN?')
	# reading_min = format(float(str(myinst.read()).strip()) * 1000, 'f')
	# print('Min: ', reading_min, ' mA')
	print('Min: {0:.4f} mA'.format(np.min(readings)))

	# Get standard dev from the readings
	# myinst.write('CALC:AVER:SDEV?')
	# reading_sdev = format(float(str(myinst.read()).strip()) * 1000, 'f')
	# print('Sdev: ', reading_sdev, ' mA')
	print('Sdev: {0:.4f} mA'.format(np.std(readings)))

	# Get count
	# myinst.write('CALC:AVER:COUN?')
	# reading_count = format(float(str(myinst.read()).strip()), '.0f')
	# print('Count: ', reading_count, ' counts')
	print('Count: ', np.count_nonzero(readings), ' counts')

	myinst.write('CALC:STAT OFF')
	myinst.write('CALC:STAT?')
	print('\nCalc Enable/Disable: ', myinst.read())

	return readings, np.mean(readings), np.max(readings), np.min(readings), np.std(readings), np.count_nonzero(readings)


def repeat_captureOnce(times, captureOnce, *args):
	readings_all = []
	for i in range(times):
		for i_readings in captureOnce(*args)[0]:
			readings_all.append(i_readings)
		# print(readings_all)
	return readings_all, np.mean(readings_all), np.max(readings_all), np.min(readings_all), np.std(
		readings_all), np.count_nonzero(readings_all)


try:
	start_time = time.time()
	# Open Connection
	# rm = visa.ResourceManager('C:\\Program Files (x86)\\IVI Foundation\\VISA\\WinNT\\agvisa\\agbin\\visa32.dll')
	rm = visa.ResourceManager()
	dmm_count = str(config['DMM'].get('DMM_count'))

	repeat_cnt_flat = int(config['Test_Case_Sample'].get('Flat_Repeat_Count'))
	trigger_cnt_flat = int(config['Test_Case_Sample'].get('Flat_Trigger_Count'))
	sample_cnt_flat = int(config['Test_Case_Sample'].get('Flat_Sample_Count'))

	repeat_cnt_pulse = int(config['Test_Case_Sample'].get('Pulse_Repeat_Count'))
	trigger_cnt_pulse = int(config['Test_Case_Sample'].get('Pulse_Trigger_Count'))
	sample_cnt_pulse = int(config['Test_Case_Sample'].get('Pulse_Sample_Count'))

	repeat_cnt_active = int(config['Test_Case_Sample'].get('Active_Repeat_Count'))
	trigger_cnt_active = int(config['Test_Case_Sample'].get('Active_Trigger_Count'))
	sample_cnt_active = int(config['Test_Case_Sample'].get('Active_Sample_Count'))

	suffix_name_list = [str(config['BASIC'].get('Excel_Sheet_Name_A')),
						str(config['BASIC'].get('Excel_Sheet_Name_B')),
						str(config['BASIC'].get('Excel_Sheet_Name_C')),
						str(config['BASIC'].get('Excel_Sheet_Name_D')),]

	visa_address_list = [str(config['DMM'].get('VISA_address_A')),
						 str(config['DMM'].get('VISA_address_B')),
						 str(config['DMM'].get('VISA_address_C')),
						 str(config['DMM'].get('VISA_address_D'))]

	myinst_name_list = []
	mythread_name_list = []
	joined_DF_name_list = []
	myinst_list = []
	mythread_list = []
	joined_DF_list = []

	# if dmm_count == '1':
	for suffix_name in suffix_name_list[0: int(dmm_count)]:
		myinst_name_list.append('{0}_{1}'.format('myinst', suffix_name))
		mythread_name_list.append('{0}_{1}'.format('mythread', suffix_name))
		joined_DF_name_list.append('{0}_{1}'.format('joined_DF', suffix_name))
	# print(myinst_name_list)
	# print(mythread_name_list)
	# print(joined_DF_name_list)

	for i in range(len(myinst_name_list)):
		myinst_name_list[i] = rm.open_resource(visa_address_list[i])
		myinst_list.append(myinst_name_list[i])

		# mythread_name_list[i] = ThreadWithReturnValue(target=repeat_captureOnce,
		#                                    args=(repeat_cnt_pulse,
		#                                          captureOnce,
		#                                          trigger_cnt_pulse,
		#                                          sample_cnt_pulse,
		#                                          myinst_list[i],))
		# mythread_list.append(mythread_name_list[i])

		joined_DF_name_list[i] = DataFrame()
		joined_DF_list.append(joined_DF_name_list[i])

	def startThread():
		for i in range(len(myinst_name_list)):
			mythread_name_list[i] = ThreadWithReturnValue(target=repeat_captureOnce,
														  args=(repeat_cnt_pulse,
																captureOnce,
																trigger_cnt_pulse,
																sample_cnt_pulse,
																myinst_list[i],))
			mythread_list.append(mythread_name_list[i])
		# print(mythread_list, '!!!!!!!')
		for i in mythread_list:
			i.start()
		# for i in mythread_list:
		# 	i.join()
		return mythread_list

	# print(myinst_list, '!!!!!!!!!')
	# print(mythread_list, '@@@@@@@@@@@')
	# print(joined_DF_list, '$$$$$$$$$$$$$$$$$$')

	queryError(myinst_list)

	dmmInit(myinst_list)

	dut = config['BASIC'].get('Dut')
	ref = config['BASIC'].get('Ref')

	for i in get_hci_bd_address():
		# print(i.keys(), i.values(), '!!!!!!!!!!!!!!!!!!!!!!')
		for j, k in i.items():
			if j == config['BASIC'].get('Dut'):
				dut_bd_address = k
			elif j == config['BASIC'].get('Ref'):
				ref_bd_address = k
			else:
				print('Something wrong with BD address. Exciting....')
				sys.exit(1)

	if str(config['BASIC'].get('Select_ChipVersion')) == '8977' or '8997' or '8987':
		logger_append.info('Chip version is selected as {0}'.format(str(config['BASIC'].get('Select_ChipVersion'))))
		# Always get deep sleep current
		cc_bt_init_status(dut, ref, 0)
		time.sleep(1)
		logger_append.info('Measuring deep sleep...')
		startThread()

		# print(mythread_list[0].join(), '!!!!!!!!!!!!!!!!!!!!!')
		# print(mythread_list[1].join(), '!!!!!!!!!!!!!!!!!!!!!')

		for i in range(int(dmm_count)):
			joined_DF_list[i] = DataFrame(resultFormat(mythread_list[i].join()),
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['Deep Sleep'])

		if str(config['Test_Case'].get('BT_Enable')) == '1':
			if str(config['Test_Case'].get('BT_Idle')) == '1':
				cc_bt_init_status(dut, ref, 0)
				cc_bt_idle()
				time.sleep(2)
				logger_append.info('Measuring BT Idle...')

				# for i in range(int(dmm_count)):
				# 	mythread_list[i].start()
				startThread()
				temp_list = []
				for i in range(int(dmm_count)):
					temp_list.append(DataFrame(resultFormat(mythread_list[i].join()),
										  index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
										  columns=['BT Idle']))
				print(temp_list, '!!!!!!!!!!!!!!!!!!!!!!!!!!')
				for i in range(int(dmm_count)):
					joined_DF_list[i] = joined_DF_list[i].join(temp_list[i])

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_Pscan')) == '1':
				cc_bt_init_status(dut, ref, 0)
				cc_bt_pscan()
				time.sleep(3)
				logger_append.info('Measuring BT Pscan...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_pscan = [float(format(results[1], '.3f')),
									float(format(results[2], '.3f')),
									float(format(results[3], '.3f')),
									float(format(results[4], '.3f')),
									float(format(results[5], '.0f'))]
				df_cc_bt_pscan = DataFrame(list_cc_bt_pscan,
										   index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
										   columns=['BT Pscan'])
				joined_result_DF = joined_result_DF.join(df_cc_bt_pscan)
				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_Iscan')) == '1':
				cc_bt_init_status(dut, ref, 0)
				cc_bt_iscan()
				time.sleep(3)
				logger_append.info('Measuring BT Iscan...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_iscan = [float(format(results[1], '.3f')),
									float(format(results[2], '.3f')),
									float(format(results[3], '.3f')),
									float(format(results[4], '.3f')),
									float(format(results[5], '.0f'))]
				df_cc_bt_iscan = DataFrame(list_cc_bt_iscan,
										   index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
										   columns=['BT Iscan'])
				joined_result_DF = joined_result_DF.join(df_cc_bt_iscan)
				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_PIscan')) == '1':
				cc_bt_init_status(dut, ref, 0)
				cc_bt_piscan()
				time.sleep(3)
				logger_append.info('Measuring BT PIscan...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_piscan = [float(format(results[1], '.3f')),
									 float(format(results[2], '.3f')),
									 float(format(results[3], '.3f')),
									 float(format(results[4], '.3f')),
									 float(format(results[5], '.0f'))]
				df_cc_bt_piscan = DataFrame(list_cc_bt_piscan,
											index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											columns=['BT PIscan'])
				joined_result_DF = joined_result_DF.join(df_cc_bt_piscan)
				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_0dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BT ACL Sniff 1.28s Master @ 0dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_acl_sniff_1dot28s_master = [float(format(results[1], '.3f')),
													   float(format(results[2], '.3f')),
													   float(format(results[3], '.3f')),
													   float(format(results[4], '.3f')),
													   float(format(results[5], '.0f'))]
				df_cc_bt_acl_sniff_1dot28s_master = DataFrame(list_cc_bt_acl_sniff_1dot28s_master,
															  index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																	 '5.Count'],
															  columns=['BT ACL Sniff 1.28S @ 0dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_acl_sniff_1dot28s_master)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_4dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(4)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BT ACL Sniff 1.28s Master @ 4dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_acl_sniff_1dot28s_master = [float(format(results[1], '.3f')),
													   float(format(results[2], '.3f')),
													   float(format(results[3], '.3f')),
													   float(format(results[4], '.3f')),
													   float(format(results[5], '.0f'))]
				df_cc_bt_acl_sniff_1dot28s_master = DataFrame(list_cc_bt_acl_sniff_1dot28s_master,
															  index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																	 '5.Count'],
															  columns=['BT ACL Sniff 1.28S @ 4dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_acl_sniff_1dot28s_master)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_12.5dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(12.5)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BT ACL Sniff 1.28s Master @ 12.5dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_acl_sniff_1dot28s_master = [float(format(results[1], '.3f')),
													   float(format(results[2], '.3f')),
													   float(format(results[3], '.3f')),
													   float(format(results[4], '.3f')),
													   float(format(results[5], '.0f'))]
				df_cc_bt_acl_sniff_1dot28s_master = DataFrame(list_cc_bt_acl_sniff_1dot28s_master,
															  index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																	 '5.Count'],
															  columns=['BT ACL Sniff 1.28S @ 12.5dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_acl_sniff_1dot28s_master)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_0dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_acl_sniff_0dot5s_master(dut_bd_address,
											  ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BT ACL Sniff 0.5s Master @ 0dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_acl_sniff_0dot5_master = [float(format(results[1], '.3f')),
													 float(format(results[2], '.3f')),
													 float(format(results[3], '.3f')),
													 float(format(results[4], '.3f')),
													 float(format(results[5], '.0f'))]
				df_cc_bt_acl_sniff_0dot5s_master = DataFrame(list_cc_bt_acl_sniff_0dot5_master,
															 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																	'5.Count'],
															 columns=['BT ACL Sniff 0.5S @ 0dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_acl_sniff_0dot5s_master)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_4dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(4)
				time.sleep(1)
				cc_bt_acl_sniff_0dot5s_master(dut_bd_address,
											  ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BT ACL Sniff 0.5s Master @ 4dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_acl_sniff_0dot5s_master = [float(format(results[1], '.3f')),
													  float(format(results[2], '.3f')),
													  float(format(results[3], '.3f')),
													  float(format(results[4], '.3f')),
													  float(format(results[5], '.0f'))]
				df_cc_bt_acl_sniff_0dot5s_master = DataFrame(list_cc_bt_acl_sniff_0dot5s_master,
															 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																	'5.Count'],
															 columns=['BT ACL Sniff 0.5S @ 4dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_acl_sniff_0dot5s_master)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_12.5dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(12.5)
				time.sleep(1)
				cc_bt_acl_sniff_0dot5s_master(dut_bd_address,
											  ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BT ACL Sniff 0.5s Master @ 12.5dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_bt_acl_sniff_0dot5s_master = [float(format(results[1], '.3f')),
													  float(format(results[2], '.3f')),
													  float(format(results[3], '.3f')),
													  float(format(results[4], '.3f')),
													  float(format(results[5], '.0f'))]
				df_cc_bt_acl_sniff_0dot5s_master = DataFrame(list_cc_bt_acl_sniff_0dot5s_master,
															 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																	'5.Count'],
															 columns=['BT ACL Sniff 0.5S @ 12.5dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_acl_sniff_0dot5s_master)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_SCO_HV3_Master_0dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(0)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				cc_bt_sco_hv3(ref_bd_address)
				time.sleep(10)
				logger_append.info('Measuring BT SCO HV3 Master @ 0dBm...')

				results = repeat_captureOnce(repeat_cnt_active, captureOnce, trigger_cnt_active, sample_cnt_active)
				list_cc_bt_sco_hv3 = [float(format(results[1], '.3f')),
									  float(format(results[2], '.3f')),
									  float(format(results[3], '.3f')),
									  float(format(results[4], '.3f')),
									  float(format(results[5], '.0f'))]
				df_cc_bt_sco_hv3 = DataFrame(list_cc_bt_sco_hv3,
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['BT SCO HV3 @ 0dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_sco_hv3)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_SCO_HV3_Master_4dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(4)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				cc_bt_sco_hv3(ref_bd_address)
				time.sleep(10)
				logger_append.info('Measuring BT SCO HV3 Master @ 4dBm...')

				results = repeat_captureOnce(repeat_cnt_active, captureOnce, trigger_cnt_active, sample_cnt_active)
				list_cc_bt_sco_hv3 = [float(format(results[1], '.3f')),
									  float(format(results[2], '.3f')),
									  float(format(results[3], '.3f')),
									  float(format(results[4], '.3f')),
									  float(format(results[5], '.0f'))]
				df_cc_bt_sco_hv3 = DataFrame(list_cc_bt_sco_hv3,
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['BT SCO HV3 @ 4dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_sco_hv3)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_SCO_HV3_Master_12.5dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(12.5)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				cc_bt_sco_hv3(ref_bd_address)
				time.sleep(10)
				logger_append.info('Measuring BT SCO HV3 Master @ 12.5dBm...')

				results = repeat_captureOnce(repeat_cnt_active, captureOnce, trigger_cnt_active, sample_cnt_active)
				list_cc_bt_sco_hv3 = [float(format(results[1], '.3f')),
									  float(format(results[2], '.3f')),
									  float(format(results[3], '.3f')),
									  float(format(results[4], '.3f')),
									  float(format(results[5], '.0f'))]
				df_cc_bt_sco_hv3 = DataFrame(list_cc_bt_sco_hv3,
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['BT SCO HV3 @ 12.5dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_sco_hv3)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_SCO_EV3_Master_0dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(0)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				cc_bt_sco_ev3(ref_bd_address)
				time.sleep(10)
				logger_append.info('Measuring BT SCO EV3 Master @ 0dBm...')

				results = repeat_captureOnce(repeat_cnt_active, captureOnce, trigger_cnt_active, sample_cnt_active)
				list_cc_bt_sco_ev3 = [float(format(results[1], '.3f')),
									  float(format(results[2], '.3f')),
									  float(format(results[3], '.3f')),
									  float(format(results[4], '.3f')),
									  float(format(results[5], '.0f'))]
				df_cc_bt_sco_ev3 = DataFrame(list_cc_bt_sco_ev3,
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['BT SCO EV3 @ 0dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_sco_ev3)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_SCO_EV3_Master_4dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(4)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				cc_bt_sco_ev3(ref_bd_address)
				time.sleep(10)
				logger_append.info('Measuring BT SCO EV3 Master @ 4dBm...')

				results = repeat_captureOnce(repeat_cnt_active, captureOnce, trigger_cnt_active, sample_cnt_active)
				list_cc_bt_sco_ev3 = [float(format(results[1], '.3f')),
									  float(format(results[2], '.3f')),
									  float(format(results[3], '.3f')),
									  float(format(results[4], '.3f')),
									  float(format(results[5], '.0f'))]
				df_cc_bt_sco_ev3 = DataFrame(list_cc_bt_sco_ev3,
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['BT SCO EV3 @ 4dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_sco_ev3)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BT_SCO_EV3_Master_12.5dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(12.5)
				time.sleep(1)
				cc_bt_acl_sniff_1dot28s_master(dut_bd_address, ref_bd_address)
				time.sleep(5)
				cc_bt_sco_ev3(ref_bd_address)
				time.sleep(10)
				logger_append.info('Measuring BT SCO EV3 Master @ 12.5dBm...')

				results = repeat_captureOnce(repeat_cnt_active, captureOnce, trigger_cnt_active, sample_cnt_active)
				list_cc_bt_sco_ev3 = [float(format(results[1], '.3f')),
									  float(format(results[2], '.3f')),
									  float(format(results[3], '.3f')),
									  float(format(results[4], '.3f')),
									  float(format(results[5], '.0f'))]
				df_cc_bt_sco_ev3 = DataFrame(list_cc_bt_sco_ev3,
											 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											 columns=['BT SCO EV3 @ 12.5dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_bt_sco_ev3)

				cc_bt_init_status(dut, ref, 0)

		elif str(config['Test_Case'].get('BT_Enable')) == '0':
			logger_append.info('Skip all BT test cases')
		else:
			logger_append.info('Invalid "BT_Enable" info, pls check config.ini file. Exiting...')
			sys.exit(1)

		if str(config['Test_Case'].get('BLE_Enable')) == '1':
			if str(config['Test_Case'].get('BLE_Adv_1.28s_3Channel_0dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(0)
				time.sleep(1)
				cc_ble_adv_1dot28s_3channel('1')
				time.sleep(3)
				logger_append.info('Measuring BLE Adv 1.28s 3-Channel @ 0dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_adv_1dot28s_3channel = [float(format(results[1], '.3f')),
													float(format(results[2], '.3f')),
													float(format(results[3], '.3f')),
													float(format(results[4], '.3f')),
													float(format(results[5], '.0f'))]
				df_cc_ble_adv_1dot28s_3channel = DataFrame(list_cc_ble_adv_1dot28s_3channel,
														   index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																  '5.Count'],
														   columns=['BLE Adv 1.28s 3-Channel @ 0dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_adv_1dot28s_3channel)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Adv_1.28s_3Channel_4dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(4)
				time.sleep(1)
				cc_ble_adv_1dot28s_3channel('1')
				time.sleep(3)
				logger_append.info('Measuring BLE Adv 1.28s 3-Channel @ 4dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_adv_1dot28s_3channel = [float(format(results[1], '.3f')),
													float(format(results[2], '.3f')),
													float(format(results[3], '.3f')),
													float(format(results[4], '.3f')),
													float(format(results[5], '.0f'))]
				df_cc_ble_adv_1dot28s_3channel = DataFrame(list_cc_ble_adv_1dot28s_3channel,
														   index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																  '5.Count'],
														   columns=['BLE Adv 1.28s 3-Channel @ 4dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_adv_1dot28s_3channel)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Adv_1.28s_3Channel_12.5dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(12.5)
				time.sleep(1)
				cc_ble_adv_1dot28s_3channel('1')
				time.sleep(3)
				logger_append.info('Measuring BLE Adv 1.28s 3-Channel @ 12.5dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_adv_1dot28s_3channel = [float(format(results[1], '.3f')),
													float(format(results[2], '.3f')),
													float(format(results[3], '.3f')),
													float(format(results[4], '.3f')),
													float(format(results[5], '.0f'))]
				df_cc_ble_adv_1dot28s_3channel = DataFrame(list_cc_ble_adv_1dot28s_3channel,
														   index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																  '5.Count'],
														   columns=['BLE Adv 1.28s 3-Channel @ 12.5dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_adv_1dot28s_3channel)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Scan_1.28s')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_ble_scan_1dot28s('1')
				time.sleep(3)
				logger_append.info('Measuring BLE Scan 1.28s...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_scan_1dot28s = [float(format(results[1], '.3f')),
											float(format(results[2], '.3f')),
											float(format(results[3], '.3f')),
											float(format(results[4], '.3f')),
											float(format(results[5], '.0f'))]
				df_cc_ble_scan_1dot28s = DataFrame(list_cc_ble_scan_1dot28s,
												   index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
												   columns=['BLE Scan 1.28s'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_scan_1dot28s)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Scan_1s')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_ble_scan_1s('1')
				time.sleep(3)
				logger_append.info('Measuring BLE Scan 1s...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_scan_1s = [float(format(results[1], '.3f')),
									   float(format(results[2], '.3f')),
									   float(format(results[3], '.3f')),
									   float(format(results[4], '.3f')),
									   float(format(results[5], '.0f'))]
				df_cc_ble_scan_1s = DataFrame(list_cc_ble_scan_1s,
											  index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
											  columns=['BLE Scan 1s'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_scan_1s)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Scan_10ms')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_ble_scan_10ms('1')
				time.sleep(3)
				logger_append.info('Measuring BLE Scan 10ms...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_scan_10ms = [float(format(results[1], '.3f')),
										 float(format(results[2], '.3f')),
										 float(format(results[3], '.3f')),
										 float(format(results[4], '.3f')),
										 float(format(results[5], '.0f'))]
				df_cc_ble_scan_10ms = DataFrame(list_cc_ble_scan_10ms,
												index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev', '5.Count'],
												columns=['BLE Scan 10ms'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_scan_10ms)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Connection_1.28s_0dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(0)
				time.sleep(1)
				cc_ble_connection_1dot28s(ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BLE Connection 1.28s @ 0dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_connection_1dot28s = [float(format(results[1], '.3f')),
												  float(format(results[2], '.3f')),
												  float(format(results[3], '.3f')),
												  float(format(results[4], '.3f')),
												  float(format(results[5], '.0f'))]
				df_cc_ble_connection_1dot28s = DataFrame(list_cc_ble_connection_1dot28s,
														 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																'5.Count'],
														 columns=['BLE Connection 1.28s @ 0dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_connection_1dot28s)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Connection_1.28s_4dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(4)
				time.sleep(1)
				cc_ble_connection_1dot28s(ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BLE Connection 1.28s @ 4dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_connection_1dot28s = [float(format(results[1], '.3f')),
												  float(format(results[2], '.3f')),
												  float(format(results[3], '.3f')),
												  float(format(results[4], '.3f')),
												  float(format(results[5], '.0f'))]
				df_cc_ble_connection_1dot28s = DataFrame(list_cc_ble_connection_1dot28s,
														 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																'5.Count'],
														 columns=['BLE Connection 1.28s @ 4dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_connection_1dot28s)

				cc_bt_init_status(dut, ref, 0)

			if str(config['Test_Case'].get('BLE_Connection_1.28s_12.5dBm')) == '1':
				cc_bt_init_status(dut, ref, 0)
				time.sleep(1)
				cc_bt_set_power_level(12.5)
				time.sleep(1)
				cc_ble_connection_1dot28s(ref_bd_address)
				time.sleep(5)
				logger_append.info('Measuring BLE Connection 1.28s @ 12.5dBm...')

				results = repeat_captureOnce(repeat_cnt_pulse, captureOnce, trigger_cnt_pulse, sample_cnt_pulse)
				list_cc_ble_connection_1dot28s = [float(format(results[1], '.3f')),
												  float(format(results[2], '.3f')),
												  float(format(results[3], '.3f')),
												  float(format(results[4], '.3f')),
												  float(format(results[5], '.0f'))]
				df_cc_ble_connection_1dot28s = DataFrame(list_cc_ble_connection_1dot28s,
														 index=['1.Average (mA)', '2.Max', '3.Min', '4.Sdev',
																'5.Count'],
														 columns=['BLE Connection 1.28s @ 12.5dBm'])

				joined_result_DF = joined_result_DF.join(df_cc_ble_connection_1dot28s)

				cc_bt_init_status(dut, ref, 0)

		elif str(config['Test_Case'].get('BLE_Enable')) == '0':
			logger_append.info('Skip all BLE test cases')
		else:
			logger_append.info('Invalid "BLE_Enable" info, pls check config.ini file')
			sys.exit(1)

		my_excel = ExcelWriter('test.xlsx')
		for i in range(int(dmm_count)):
			joined_DF_list[i].T.to_excel(my_excel, sheet_name=suffix_name_list[i], index=True)
		my_excel.save()

	else:
		logger_append.info('Invalid chip version info, pls check config.ini file.')
		sys.exit(1)

	# util.get_debug_info()
	checkOPC(myinst_list)
	queryError(myinst_list)

	# Close Connection
	for i in myinst_list:
		i.write('DISP:TEXT "Complete..."')
		i.close()
		logger_append.info('Close instrument connection.')

	logger_append.info('\n--- {0} seconds | {1} minutes ---'.format(format((time.time() - start_time), '.2f'),
																  format((time.time() - start_time) / 60, '.2f')))

except Exception as err:
	print('Exception: ' + str(err.message))
	sys.exit(1)

finally:
	# perform clean up operations
	print('\n=== Complete ===\n')
