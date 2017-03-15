#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import sys
from collections import OrderedDict

from pandas import DataFrame

import src.my_misc.my_time as my_time
import src.my_config.config_basic as config_basic
import src.my_dmm.dmm_basic as dmm_basic
import src.my_excel.excel_basic as excel_basic
import src.my_excel.excel_format as excel_format
import src.my_ssh.ssh_get_cmd as ssh_get_cmd
import src.my_ssh.ssh_send_cmd as ssh_send_cmd


def visa_address():
	"""
	Get VISA address list based on running instrument number and their addresses from config file
	:return: VISA address list
	"""
	# Init config file
	config = config_basic.load_config()
	# Get config file instrument count (DMM count): how many DMM are connected and measuring data
	dmm_count = int(str(config['DMM'].get('DMM_Count')))
	# Get config file DMM VISA address
	visa_address_list_all = [str(config['DMM'].get('VISA_Address_A')),
	                         str(config['DMM'].get('VISA_Address_B')),
	                         str(config['DMM'].get('VISA_Address_C')),
	                         str(config['DMM'].get('VISA_Address_D'))]

	# Append VISA address to a list and return
	visa_address_list = []
	for i in range(int(dmm_count)):
		visa_address_list.append(visa_address_list_all[i])

	return visa_address_list


def starter(enable_print=1):
	start_str = '''
	================================================================
	Program starts @ {0}
	----------------------------------------------------------------
	'''
	if enable_print == 1:
		start_time = my_time.now()
		print(start_str.format(my_time.now_formatted(start_time)))
	else:
		start_time = my_time.now()
		return start_time, my_time.now_formatted(start_time)


def ender(enable_print=1):
	end_str = '''
	----------------------------------------------------------------
	Program ends @ {0}
	================================================================
	'''
	if enable_print == 1:
		end_time = my_time.now()
		print(end_str.format(my_time.now_formatted(end_time)))
	else:
		end_time = my_time.now()
		return end_time, my_time.now_formatted(end_time)


def run_time(start_time, end_time, enable_print=1):
	run_time_str = '''
	----------------------------------------------------------------
	Program total running time: {0}
	================================================================
	'''
	if enable_print == 1:
		delta_time = my_time.time_delta(start_time, end_time)
		print(run_time_str.format(delta_time))
	else:
		delta_time = my_time.time_delta(start_time, end_time)
		return delta_time


def test_case_init_wrapper(case_name, case_func, *args, **kwargs):
	print('Measuring {0}......'.format(case_name))
	case_func(*args, **kwargs)
	data_frame_list = dmm_basic.dmm_flow_wrapper(visa_address(),
	                                             600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
	                                             1, 100, case_name, 0)
	return data_frame_list


def test_case_wrapper(case_name, joined_df_list, enable, case_func, *args, **kwargs):
	enable = int(str(enable))
	if enable == 1:
		print('Measuring {0}......'.format(case_name))
		case_func(*args, **kwargs)
		data_frame_list = dmm_basic.dmm_flow_wrapper(visa_address(),
		                                             600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
		                                             1, 100, case_name, 0)
		for i in range(len(visa_address())):
			joined_df_list[i] = joined_df_list[i].join(data_frame_list[i])
		return joined_df_list
	else:
		print('Skip <{0}> ......'.format(case_name))
		return joined_df_list


def main_flow():
	starter(1)
	start_time = starter(0)[0]
	start_time_formatted = starter(0)[1]

	# Design joined data frame list based on connected Inst number, and init with empty DataFrame()
	joined_df_list = []
	for i in range(len(visa_address())):
		joined_df_list.append(DataFrame())

	config = config_basic.load_config()
	dut = config_basic.config_dut()
	ref = config_basic.config_ref()
	dut_bd_addr = ssh_get_cmd.bd_addr()[0]
	ref_bd_addr = ssh_get_cmd.bd_addr()[1]

	if str(config['BASIC'].get('Chip_Version')) == '8977' or '8997' or '8987':
		# Print chip version
		print('Chip version is selected as {0}'.format(str(config['BASIC'].get('Chip_Version'))))

		# Get case_0 return data frame list: [inst_1_data_frame, inst_2_data_frame, ...]
		case_0_data_frame_list = test_case_init_wrapper('Deep Sleep', ssh_send_cmd.cc_bt_init_status, dut, ref, 0)

		# Assign first data frame list to joined data frame list as initiate value
		for i in range(len(visa_address())):
			joined_df_list[i] = case_0_data_frame_list[i]

		if str(config['Test_Case'].get('BT_Enable')) == '1':
			# Get case_1 return data frame list: [inst_1_data_frame, inst_2_data_frame, ...]
			joined_df_list = test_case_wrapper('BT Idle', joined_df_list,
			                                           config['Test_Case'].get('BT_Idle'),
			                                           ssh_send_cmd.cc_bt_idle, dut, ref, 0)

			joined_df_list = test_case_wrapper('BT Page Scan', joined_df_list,
			                                           config['Test_Case'].get('BT_P_Scan'),
			                                           ssh_send_cmd.cc_bt_pscan, dut, ref, 0)

			joined_df_list = test_case_wrapper('BT Inquiry Scan', joined_df_list,
			                                           config['Test_Case'].get('BT_I_Scan'),
			                                           ssh_send_cmd.cc_bt_iscan, dut, ref, 0)

			joined_df_list = test_case_wrapper('BT Page & Inquiry Scan', joined_df_list,
			                                           config['Test_Case'].get('BT_PI_Scan'),
			                                           ssh_send_cmd.cc_bt_piscan, dut, ref, 0)

			joined_df_list = test_case_wrapper('BT ACL Sniff 1.28s interval Master @ 0dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_0-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_acl_sniff_1dot28s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_df_list = test_case_wrapper('BT ACL Sniff 1.28s interval Master @ 4dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_4-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_acl_sniff_1dot28s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_df_list = test_case_wrapper('BT ACL Sniff 1.28s interval Master @ Max dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_Max-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_acl_sniff_1dot28s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')

			joined_df_list = test_case_wrapper('BT ACL Sniff 0.5s interval Master @ 0 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_0-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_acl_sniff_0dot5s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_df_list = test_case_wrapper('BT ACL Sniff 0.5s interval Master @ 4 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_4-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_acl_sniff_0dot5s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_df_list = test_case_wrapper('BT ACL Sniff 0.5s interval Master @ Max dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_Max-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_acl_sniff_0dot5s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')

			joined_df_list = test_case_wrapper('BT SCO HV3 Master @ 0 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_SCO_HV3_Master_0-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_sco_hv3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_df_list = test_case_wrapper('BT SCO HV3 Master @ 4 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_SCO_HV3_Master_4-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_sco_hv3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_df_list = test_case_wrapper('BT SCO HV3 Master @ Max dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_SCO_HV3_Master_Max-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_sco_hv3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')

			joined_df_list = test_case_wrapper('BT SCO EV3 Master @ 0 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_SCO_EV3_Master_0-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_sco_ev3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_df_list = test_case_wrapper('BT SCO EV3 Master @ 4 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_SCO_EV3_Master_4-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_sco_ev3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_df_list = test_case_wrapper('BT SCO EV3 Master @ Max dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BT_SCO_EV3_Master_Max-dBm-pin'),
			                                           ssh_send_cmd.cc_bt_sco_ev3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')
		elif str(config['Test_Case'].get('BT_Enable')) == '0':
			print('Skip all BT test cases')
		else:
			print('Invalid "BT_Enable" info, pls check config.ini file. Exiting...')
			sys.exit(1)

		if str(config['Test_Case'].get('BLE_Enable')) == '1':
			joined_df_list = test_case_wrapper('BLE Adv 1.28s interval 3 channels @ 0 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Adv_1.28s_3Channel_0-dBm-pin'),
			                                           ssh_send_cmd.cc_ble_adv_1dot28s_3channel,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_df_list = test_case_wrapper('BLE Adv 1.28s interval 3 channels @ 4 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Adv_1.28s_3Channel_4-dBm-pin'),
			                                           ssh_send_cmd.cc_ble_adv_1dot28s_3channel,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_df_list = test_case_wrapper('BLE Adv 1.28s interval 3 channels @ Max dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Adv_1.28s_3Channel_Max-dBm-pin'),
			                                           ssh_send_cmd.cc_ble_adv_1dot28s_3channel,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_df_list = test_case_wrapper('BLE Scan 1.28s interval',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Scan_1.28s'),
			                                           ssh_send_cmd.cc_ble_scan_1dot28s,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_df_list = test_case_wrapper('BLE Scan 1s interval',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Scan_1s'),
			                                           ssh_send_cmd.cc_ble_scan_1s,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_df_list = test_case_wrapper('BLE Scan 10ms interval',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Scan_10ms'),
			                                           ssh_send_cmd.cc_ble_scan_10ms,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_df_list = test_case_wrapper('BLE Connection 1.28s interval @ 0 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Connection_1.28s_0-dBm-pin'),
			                                           ssh_send_cmd.cc_ble_connection_1dot28s,
			                                           dut,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_df_list = test_case_wrapper('BLE Connection 1.28s interval @ 4 dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Connection_1.28s_4-dBm-pin'),
			                                           ssh_send_cmd.cc_ble_connection_1dot28s,
			                                           dut,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_df_list = test_case_wrapper('BLE Connection 1.28s interval @ Max dBm at Pin',
			                                           joined_df_list,
			                                           config['Test_Case'].get('BLE_Connection_1.28s_Max-dBm-pin'),
			                                           ssh_send_cmd.cc_ble_connection_1dot28s,
			                                           dut,
			                                           ref, ref_bd_addr,
			                                           'Max')
		elif str(config['Test_Case'].get('BLE_Enable')) == '0':
			print('Skip all BLE test cases')
		else:
			print('Invalid "BLE_Enable" info, pls check config.ini file')
			sys.exit(1)

	# print(joined_df_list)

	ender(1)
	end_time = ender(0)[0]
	end_time_formatted = ender(0)[1]

	delta_time = run_time(start_time, end_time, 0)
	run_time(start_time, end_time, 1)

	# Write to different sheet
	excel_sheet_name_list = [str(config['BASIC'].get('Excel_Sheet_Name_A')),
	                         str(config['BASIC'].get('Excel_Sheet_Name_B')),
	                         str(config['BASIC'].get('Excel_Sheet_Name_C')),
	                         str(config['BASIC'].get('Excel_Sheet_Name_D')), ]

	df_version = DataFrame(OrderedDict((('WLAN Version', ['xx.xx.xx.xx.xx.xx']),
	                                    ('BT Version', ['xx.xx.xx.xx.xx.xx']),
	                                    ('Hardware', ['Robin3 WIB module']),
	                                    ('DUT MAC address', ['xx.xx.xx.xx.xx.xx']),
	                                    ('DUT BD address', [dut_bd_addr]),
	                                    ('REF BD address', [ref_bd_addr]),
	                                    ('Test Engineer', ['Alex Wang']),
	                                    ('Start Time', [start_time_formatted]),
	                                    ('End Time', [end_time_formatted]),
	                                    ('Run Time', [delta_time]))))
	sheet_version = 'Version'

	excel_writer = excel_basic.open_excel('test.xlsx')

	excel_basic.write_excel(excel_writer, df_version, sheet_name=sheet_version)

	workbook = excel_writer.book
	worksheet_version = excel_writer.sheets[sheet_version]

	excel_format.set_column_width(worksheet_version, 'B', 'B', 18)
	excel_format.set_column_width(worksheet_version, 'C', 'C', 88)

	format_title_one = excel_format.format_title_one(workbook)
	format_title_two = excel_format.format_title_two(workbook)
	worksheet_version.merge_range('B2:C2', 'Information', format_title_one)

	format_index_one = excel_format.format_index_one(workbook)
	format_content_one = excel_format.format_content_one(workbook)
	format_content_two = excel_format.format_content_two(workbook)

	# cell_index_version = ['B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12']
	# cell_content_version = ['C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12']
	cell_index_version = []
	cell_content_version = []
	for i in range(len(df_version.columns.values)):
		cell_index_version.append('B{0}'.format(i+3))
		cell_content_version.append('C{0}'.format(i+3))

	for i in range(len(df_version.columns.values)):
		excel_basic.write_excel_format(worksheet_version,
		                               cell_index_version[i],
		                               df_version.columns.values[i],
		                               format_index_one)
		excel_basic.write_excel_format(worksheet_version,
		                               cell_content_version[i],
		                               df_version[df_version.columns.values[i]].values[0],
		                               format_content_one)
		# worksheet_version.write(cell_index_version[i],
		#                         df_version.columns.values[i],
		#                         format_index_one)
		# worksheet_version.write(cell_content_version[i],
		#                         df_version[df_version.columns.values[i]].values[0],
		#                         format_content_one)


	for i in range(len(visa_address())):
		# Convert the dataframe to an XlsxWriter Excel object.
		excel_basic.write_excel(excel_writer, joined_df_list[i], excel_sheet_name_list[i])
	worksheet_data_list = []
	for i in range(len(visa_address())):
		worksheet_data_list.append(excel_writer.sheets[excel_sheet_name_list[i]])
	for i in worksheet_data_list:
		excel_format.set_column_width(i, 'B', 'B', 18)
		excel_format.set_column_width(i, 'C', 'H', 14)
	cell_index_data = []
	cell_column_data = []
	cell_content_data = []
	cell_content_data_array = []
	for i_index in range(len(joined_df_list[0].T.index.values)):
		cell_index_data.append('B{0}'.format(i_index+3))

	for i_column in range(len(joined_df_list[0].T.columns.values)):
		cell_column_data.append('{0}2'.format(excel_basic.excel_col2str(i_column+excel_basic.excel_col2num('C'))))
	# print(cell_column_data, '!!!!!!!!')
	for i_index in range(len(joined_df_list[0].T.index.values)):
		for i_column in range(len(joined_df_list[0].T.columns.values)):
			cell_content_data.append('{0}{1}'.format(excel_basic.excel_col2str(i_column + excel_basic.excel_col2num('C')),
			                                         i_index + 3))
		cell_content_data_array.append(cell_content_data)
		cell_content_data = []
	print(cell_content_data_array)

	# Loop for data worksheet
	for i_worksheet in worksheet_data_list:

		# Get index count, which is test cases count
		for i_index in range(len(joined_df_list[0].T.index.values)):
			# Get column count
			for i_column in range(len(joined_df_list[0].T.columns.values)):
				i_worksheet.write(cell_column_data[i_column], joined_df_list[worksheet_data_list.index(i_worksheet)].T.columns.values[i_column], format_title_two)
				# worksheet_data_list.index(i_worksheet) is the one rail data frame in DF list, since worksheet # = DF #
				i_worksheet.write(cell_index_data[i_index],
				        joined_df_list[worksheet_data_list.index(i_worksheet)].T.index.values[i_index],
				                  format_index_one)
				i_worksheet.write(cell_content_data_array[i_index][i_column],
				                  joined_df_list[worksheet_data_list.index(i_worksheet)].T.get_value(joined_df_list[worksheet_data_list.index(i_worksheet)].T.index.values[i_index], joined_df_list[worksheet_data_list.index(i_worksheet)].T.columns.values[i_column]),
				                  format_content_two)


	excel_basic.close_workbook(workbook)
	excel_basic.close_excel(excel_writer)
