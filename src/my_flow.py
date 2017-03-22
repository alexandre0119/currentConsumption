#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import sys
# Ordered dict to construct DF
from collections import OrderedDict
from pandas import DataFrame
# DF related
import src.my_misc.dataframe_basic as df_basic
# config.ini settings
import src.my_config.config_basic as config_basic
# DMM control related
import src.my_dmm.dmm_basic as dmm_basic
# Excel related
import src.my_excel.excel_basic as excel_basic
import src.my_excel.excel_format as excel_format
# Time related
import src.my_misc.my_time as my_time
# SSH related
import src.my_ssh.ssh_get_cmd as ssh_get_cmd
import src.my_ssh.ssh_send_cmd as ssh_send_cmd
# Decorator
import src.my_misc.my_decorator as my_decorator


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
	data_frame_list = dmm_basic.dmm_flow_wrapper(config_basic.visa_address_active_list(),
	                                             600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
	                                             1, 100, case_name, 0)
	return data_frame_list


def test_case_wrapper(case_name, joined_df_list, enable, case_func, *args, **kwargs):
	enable = int(str(enable))
	if enable == 1:
		print('Measuring {0}......'.format(case_name))
		case_func(*args, **kwargs)
		data_frame_list = dmm_basic.dmm_flow_wrapper(config_basic.visa_address_active_list(),
		                                             600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
		                                             1, 100, case_name, 0)
		for i in range(len(config_basic.visa_address_active_list())):
			joined_df_list[i] = joined_df_list[i].join(data_frame_list[i])
		return joined_df_list
	else:
		print('Skip <{0}> ......'.format(case_name))
		return joined_df_list


def main_flow():
	my_decorator.main_flow_starter(1)
	start_time = my_decorator.main_flow_starter(0)[0]
	start_time_formatted = my_decorator.main_flow_starter(0)[1]

	# Design joined data frame list based on connected Inst number, and init with empty DataFrame()
	joined_df_list = []
	for i in range(len(config_basic.visa_address_active_list())):
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
		for i in range(len(config_basic.visa_address_active_list())):
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

	my_decorator.main_flow_ender(1)
	end_time = my_decorator.main_flow_ender(0)[0]
	end_time_formatted = my_decorator.main_flow_ender(0)[1]

	delta_time = run_time(start_time, end_time, 0)
	run_time(start_time, end_time, 1)

	# [Start][Excel] write data to Excel

	# [Open][Excel] open excel file
	excel_writer = excel_basic.open_excel('test.xlsx')
	# Create workbook object
	workbook = excel_writer.book

	# [Start][Worksheet][version]

	# [Worksheet][Name] version information sheet
	sheet_version = 'Version'

	# [Worksheet][version] create DF 'df_version' based on ordered dict
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

	# [Worksheet][version] Write raw data to excel without format, swap column and index
	excel_basic.write_excel(excel_writer, df_version, sheet_name=sheet_version)

	# [Worksheet][version] worksheet object
	worksheet_version = excel_writer.sheets[sheet_version]

	# [Worksheet][version][format] set column width
	excel_format.set_column_width(worksheet_version, 'B', 'B', 18)
	excel_format.set_column_width(worksheet_version, 'C', 'C', 88)

	# [Worksheet][version][format] write and format title
	format_title_one = excel_format.format_title_one(workbook)
	worksheet_version.merge_range('B2:C2', 'Information', format_title_one)

	# [Worksheet][version][format] format index
	format_index_one = excel_format.format_index_one(workbook)
	# [Worksheet][version][format] format content
	format_content_one = excel_format.format_content_one(workbook)

	# [version] Get DataFrame column list length for 'df_version'
	df_version_col_len = len(df_basic.get_col(df_version))

	# [version] Create index cell list
	cell_version_index = excel_basic.create_single_col('B', '3', df_version_col_len)
	# [version] Create index content cell list
	cell_version_content = excel_basic.create_single_col('C', '3', df_version_col_len)

	# [version][write] Loop for DF 'df_version' column length
	for i in range(df_version_col_len):
		# Write DF 'df_version' each column to cell destination
		excel_basic.write_excel_format(worksheet_version,
		                               cell_version_index[i],
		                               df_basic.get_col(df_version)[i],
		                               format_index_one)
		# Write DF 'df_version' each column corresponding data to cell destination
		excel_basic.write_excel_format(worksheet_version,
		                               cell_version_content[i],
		                               df_basic.get_col_value(df_version, df_basic.get_col(df_version)[i]),
		                               format_content_one)

	# [Complete][Worksheet][version]

	# [Start][Worksheet][data]

	# [Worksheet][data] Create worksheet object list
	# Worksheet for data name list, all up to 4 sheets based on config.ini file
	excel_sheet_name_list = config_basic.worksheet_name_all_list()
	# Loop for VISA address, how many instruments we are using now
	for i in range(len(config_basic.visa_address_active_list())):
		# Convert the dataframe to an XlsxWriter Excel object.
		excel_basic.write_excel(excel_writer, joined_df_list[i], excel_sheet_name_list[i])
	# Create worksheet object list
	worksheet_data_list = []
	for i in range(len(config_basic.visa_address_active_list())):
		worksheet_data_list.append(excel_writer.sheets[excel_sheet_name_list[i]])

	# [Worksheet][data][format] format title
	format_title_two = excel_format.format_title_two(workbook)
	# [Worksheet][data][format] format content
	format_content_two = excel_format.format_content_two(workbook)

	# [data] Get DataFrame index list length for 'joined_df_list'
	joined_df_list_idx_len = len(df_basic.get_idx(joined_df_list[0].T))
	# [data] Get DataFrame column list length for 'joined_df_list'
	joined_df_list_col_len = len(df_basic.get_col(joined_df_list[0].T))

	# [data] Set column width for each worksheet
	for i in worksheet_data_list:
		excel_format.set_column_width(i, 'B', 'B', 18)
		excel_format.set_column_width(i, 'C', 'H', 14)

	# [data] Create index cell list
	cell_data_index = excel_basic.create_single_col('B', '3', joined_df_list_idx_len)
	# [data] Create title cell list
	cell_data_title = excel_basic.create_single_row('C', '2', joined_df_list_col_len)
	# [data] Create content cell list
	cell_data_content_array = excel_basic.create_array('C', '3', joined_df_list_col_len, joined_df_list_idx_len)

	# [data][write] Loop for data worksheet
	for i_worksheet in worksheet_data_list:
		# Get index count, which is test cases count
		for i_index in range(joined_df_list_idx_len):
			# Get column count
			for i_column in range(joined_df_list_col_len):
				# worksheet_data_list.index(i_worksheet) is the one rail dataframe in DF list, since worksheet # = DF #
				i_dataframe = joined_df_list[worksheet_data_list.index(i_worksheet)].T
				# [Worksheet][data] write title
				excel_basic.write_excel_format(i_worksheet,
				                               cell_data_title[i_column],
				                               df_basic.get_col(i_dataframe)[i_column],
				                               format_title_two)
				# [Worksheet][data] write index
				excel_basic.write_excel_format(i_worksheet,
				                               cell_data_index[i_index],
				                               df_basic.get_idx(i_dataframe)[i_index],
				                               format_index_one)
				# [Worksheet][data] write content
				excel_basic.write_excel_format(i_worksheet,
				                               cell_data_content_array[i_index][i_column],
				                               df_basic.get_idx_col_value(i_dataframe,
				                                                          df_basic.get_idx(i_dataframe)[i_index],
				                                                          df_basic.get_col(i_dataframe)[i_column]),
				                               format_content_two)

	# [Complete][Worksheet][data]

	# Close workbook object
	excel_basic.close_workbook(workbook)
	# Close excel object
	excel_basic.close_excel(excel_writer)
