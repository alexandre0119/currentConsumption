#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_time as my_time
import src.my_dmm as my_dmm
import src.my_excel as my_excel
import src.my_ssh as my_ssh
import configparser
from pandas import DataFrame, ExcelWriter


def load_config(config_name):
	config = configparser.ConfigParser()
	config.read(config_name)
	return config

def visa_address():
	"""
	Get VISA address list based on running instrument number
	:return: VISA address list
	"""
	config = load_config('config.ini')

	dmm_count = int(str(config['DMM'].get('DMM_count')))
	visa_address_list_all = [str(config['DMM'].get('VISA_address_A')),
	                         str(config['DMM'].get('VISA_address_B')),
	                         str(config['DMM'].get('VISA_address_C')),
	                         str(config['DMM'].get('VISA_address_D'))]

	visa_address_list = []

	for i in range(int(dmm_count)):
		visa_address_list.append(visa_address_list_all[i])

	return visa_address_list


def starter():
	start_str = '''
	================================================
	Program starts @ {0}
	------------------------------------------------
		'''
	print(start_str.format(my_time.now_formatted()))
	start_time = my_time.now()
	return start_time


def ender():
	end_str = '''
	------------------------------------------------
	Program ends @ {0}
	================================================
	'''
	end_time = my_time.now()
	print(end_str.format(my_time.now_formatted()))
	return end_time


def run_time(start_time, end_time):
	run_time_str = '''
	------------------------------------------------
	Program total running time: {0}
	================================================
	'''
	delta_time = my_time.time_delta(start_time, end_time)
	print(run_time_str.format(delta_time))
	return delta_time


def test_case_wrapper(case_name, case_func, enable):
	enable = int(enable)
	if enable == 1:
		print('Measuring {0}......'.format(case_name))
		case_func = case_func
		data_frame_list = my_dmm.dmm_flow_wrapper(visa_address(),
		                                     600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
		                                     1, 10, case_name, 0)
		return data_frame_list
	else:
		print('Skip {0}......'.format(case_name))


def main_flow():
	start_time = starter()

	# Design joined data frame list based on connected Inst number, and init with empty DataFrame()
	joined_data_frame_list = []
	for i in range(len(visa_address())):
		joined_data_frame_list.append(DataFrame())

	config = load_config('config.ini')
	dut = config['BASIC'].get('Dut')
	ref = config['BASIC'].get('Ref')

	if str(config['BASIC'].get('Select_ChipVersion')) == '8977' or '8997' or '8987':
		# Print chip version
		print('Chip version is selected as {0}'.format(str(config['BASIC'].get('Select_ChipVersion'))))
		# Get case_0 return data frame list: [inst_1_data_frame, inst_2_data_frame, ...]
		case_0_data_frame_list = test_case_wrapper('case_0', 'case_func', 1)
		# Assign first data frame list to joined data frame list as initiate value
		for i in range(len(visa_address())):
			joined_data_frame_list[i] = case_0_data_frame_list[i]

		if str(config['Test_Case'].get('BT_Enable')) == '1':
			# Get case_1 return data frame list: [inst_1_data_frame, inst_2_data_frame, ...]
			if str(config['Test_Case'].get('BT_Idle')) == '1':
				# cc_bt_init_status = my_ssh.cc_bt_init_status(dut, ref, 0)
				case_1_data_frame_list = test_case_wrapper('case_1', 'case_func', 1)
				for i in range(len(visa_address())):
					joined_data_frame_list[i] = joined_data_frame_list[i].join(case_1_data_frame_list[i])
			else:
				test_case_wrapper('case_1', 'case_func', 0)

			if str(config['Test_Case'].get('BT_Pscan')) == '1':
				case_2_data_frame_list = test_case_wrapper('case_2', 'case_func', 1)
				for i in range(len(visa_address())):
					joined_data_frame_list[i] = joined_data_frame_list[i].join(case_2_data_frame_list[i])
			else:
				test_case_wrapper('case_2', 'case_func', 0)

	print(joined_data_frame_list)

	# Write to different sheet
	excel_sheet_name_list = [str(config['BASIC'].get('Excel_Sheet_Name_A')),
	                    str(config['BASIC'].get('Excel_Sheet_Name_B')),
	                    str(config['BASIC'].get('Excel_Sheet_Name_C')),
	                    str(config['BASIC'].get('Excel_Sheet_Name_D')), ]

	my_excel_obj = my_excel.open_excel('test.xlsx')

	for i in range(len(visa_address())):
		my_excel.write_excel(my_excel_obj, joined_data_frame_list[i], excel_sheet_name_list[i], True)

	my_excel.save_excel(my_excel_obj)

	end_time = ender()
	run_time(start_time, end_time)
