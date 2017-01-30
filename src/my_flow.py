#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_time as my_time
import src.my_dmm as my_dmm
import src.my_excel as my_excel
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

	joined_data_frame_list = []
	raw_data_frame_list = []
	for i in range(len(visa_address())):
		joined_data_frame_list.append(DataFrame())

	config = load_config('config.ini')

	if str(config['BASIC'].get('Select_ChipVersion')) == '8977' or '8997' or '8987':
		print('Chip version is selected as {0}'.format(str(config['BASIC'].get('Select_ChipVersion'))))
		case_0_data_frame_list = test_case_wrapper('case_0', 'case_func', 1)
		for i in range(len(visa_address())):
			joined_data_frame_list[i] = case_0_data_frame_list[i]

		if str(config['Test_Case'].get('BT_Enable')) == '1':

			case_1_data_frame_list = test_case_wrapper('case_1', 'case_func', 1)
			raw_data_frame_list.append(case_1_data_frame_list)

			case_2_data_frame_list = test_case_wrapper('case_2', 'case_func', 1)
			raw_data_frame_list.append(case_2_data_frame_list)

			case_3_data_frame_list = test_case_wrapper('case_3', 'case_func', 1)
			raw_data_frame_list.append(case_3_data_frame_list)

	for i_visa_address in range(len(visa_address())):
		for i_data_frame in raw_data_frame_list:
			joined_data_frame_list[i] = joined_data_frame_list[i].join(i_data_frame[i_visa_address])

	excel_sheet_name_list = ['3_3', '1_8']

	my_excel_obj = my_excel.open_excel('test.xlsx')

	for i in range(len(visa_address())):
		my_excel.write_excel(my_excel_obj, joined_data_frame_list[i], excel_sheet_name_list[i], True)

	my_excel.save_excel(my_excel_obj)

	end_time = ender()
	run_time(start_time, end_time)
