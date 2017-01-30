#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_time as my_time
import src.my_dmm as my_dmm
import configparser
from pandas import DataFrame, ExcelWriter

def visa_address():
	"""
	Get VISA address list based on running instrument number
	:return: VISA address list
	"""
	config = configparser.ConfigParser()
	config.read('config.ini')

	dmm_count = int(str(config['DMM'].get('DMM_count')))
	visa_address_list_all = [str(config['DMM'].get('VISA_address_A')),
							 str(config['DMM'].get('VISA_address_B')),
							 str(config['DMM'].get('VISA_address_C')),
							 str(config['DMM'].get('VISA_address_D'))]

	visa_address_list = []

	for i in range(int(dmm_count)):
		visa_address_list.append(visa_address_list_all[i])

	return visa_address_list


def main_flow():
	start_str = '''
================================================
Program starts @ {0}
------------------------------------------------
	'''
	print(start_str.format(my_time.now_formatted()))
	start_time = my_time.now()

	# print(visa_address())
	my_inst_list = my_dmm.open_connection(visa_address())
	# my_dmm.query_error(my_inst_list, 1)
	# my_dmm.check_opc(my_inst_list, 1)
	# my_dmm.get_idn(my_inst_list, 1)
	my_dmm.text_display(my_inst_list, 'Running...')
	my_dmm.dmm_init(my_inst_list, 600000, 3, 'IMM', 'MIN', 'TIM', 'MIN', 0)

	joined_dataframe_list = []
	for i in my_inst_list:
		reading = my_dmm.measure_single_dmm(i, 1, 10, 0)
		reading = my_dmm.dmm_reading_format(reading)
		joined_dataframe = my_dmm.join_dataframe('Test', reading)
		joined_dataframe_list.append(joined_dataframe)
		print(joined_dataframe)
		print('\n')

	my_excel = ExcelWriter('test.xlsx')
	for i in joined_dataframe_list:
		i.T.to_excel(my_excel, sheet_name='test', index=True)
	my_excel.save()

	# Close connection
	my_dmm.close_connection(my_inst_list)
	# Calculate time
	end_time = my_time.now()
	delta_time = my_time.time_delta(start_time, end_time)
	end_str = '''
------------------------------------------------
Program ends @ {0}
Program total running time: {1}
================================================
	'''
	print(end_str.format(my_time.now_formatted(), delta_time))
