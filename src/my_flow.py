#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_time as my_time
import src.my_dmm as my_dmm
import src.my_excel as my_excel
import src.my_ssh as my_ssh
import src.my_bt_case as my_bt_case
import src.my_config as my_config
import src.my_ssh_send_cmd as my_ssh_send_cmd
import src.my_ssh_get_cmd as my_ssh_get_cmd
from pandas import DataFrame, ExcelWriter
import sys


def visa_address():
	"""
	Get VISA address list based on running instrument number and their addresses from config file
	:return: VISA address list
	"""
	# Init config file
	config = my_config.load_config('config.ini')
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


def starter():
	start_str = '''
	================================================================
	Program starts @ {0}
	----------------------------------------------------------------
		'''
	print(start_str.format(my_time.now_formatted()))
	start_time = my_time.now()
	return start_time


def ender():
	end_str = '''
	----------------------------------------------------------------
	Program ends @ {0}
	================================================================
	'''
	end_time = my_time.now()
	print(end_str.format(my_time.now_formatted()))
	return end_time


def run_time(start_time, end_time):
	run_time_str = '''
	----------------------------------------------------------------
	Program total running time: {0}
	================================================================
	'''
	delta_time = my_time.time_delta(start_time, end_time)
	print(run_time_str.format(delta_time))
	return delta_time


def test_case_init_wrapper(case_name, case_func, *args, **kwargs):
	print('Measuring {0}......'.format(case_name))
	case_func(*args, **kwargs)
	data_frame_list = my_dmm.dmm_flow_wrapper(visa_address(),
	                                          600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
	                                          1, 10, case_name, 0)
	return data_frame_list


def test_case_wrapper(case_name, joined_data_frame_list, enable, case_func, *args, **kwargs):
	enable = int(str(enable))
	if enable == 1:
		print('Measuring {0}......'.format(case_name))
		case_func(*args, **kwargs)
		data_frame_list = my_dmm.dmm_flow_wrapper(visa_address(),
		                                          600000, 3, 'IMM', 'MIN', 'TIM', 'MIN',
		                                          1, 10, case_name, 0)
		for i in range(len(visa_address())):
			joined_data_frame_list[i] = joined_data_frame_list[i].join(data_frame_list[i])
		return joined_data_frame_list
	else:
		print('Skip <{0}> ......'.format(case_name))
		return joined_data_frame_list


def main_flow():
	start_time = starter()

	# Design joined data frame list based on connected Inst number, and init with empty DataFrame()
	joined_data_frame_list = []
	for i in range(len(visa_address())):
		joined_data_frame_list.append(DataFrame())

	config = my_config.load_config('config.ini')
	dut = my_config.config_dut()
	ref = my_config.config_ref()
	dut_bd_addr = my_ssh_get_cmd.bd_addr()[0]
	ref_bd_addr = my_ssh_get_cmd.bd_addr()[1]

	if str(config['BASIC'].get('Chip_Version')) == '8977' or '8997' or '8987':
		# Print chip version
		print('Chip version is selected as {0}'.format(str(config['BASIC'].get('Chip_Version'))))

		# Get case_0 return data frame list: [inst_1_data_frame, inst_2_data_frame, ...]
		case_0_data_frame_list = test_case_init_wrapper('Deep Sleep', my_ssh_send_cmd.cc_bt_init_status, dut, ref, 0)

		# Assign first data frame list to joined data frame list as initiate value
		for i in range(len(visa_address())):
			joined_data_frame_list[i] = case_0_data_frame_list[i]


		if str(config['Test_Case'].get('BT_Enable')) == '1':
			# Get case_1 return data frame list: [inst_1_data_frame, inst_2_data_frame, ...]
			joined_data_frame_list = test_case_wrapper('BT Idle', joined_data_frame_list,
			                                           config['Test_Case'].get('BT_Idle'),
			                                           my_ssh_send_cmd.cc_bt_idle, dut, ref, 0)

			joined_data_frame_list = test_case_wrapper('BT Page Scan', joined_data_frame_list,
			                                           config['Test_Case'].get('BT_P_Scan'),
			                                           my_ssh_send_cmd.cc_bt_pscan, dut, ref, 0)

			joined_data_frame_list = test_case_wrapper('BT Inquiry Scan', joined_data_frame_list,
			                                           config['Test_Case'].get('BT_I_Scan'),
			                                           my_ssh_send_cmd.cc_bt_iscan, dut, ref, 0)

			joined_data_frame_list = test_case_wrapper('BT Page & Inquiry Scan', joined_data_frame_list,
			                                           config['Test_Case'].get('BT_PI_Scan'),
			                                           my_ssh_send_cmd.cc_bt_piscan, dut, ref, 0)

			joined_data_frame_list = test_case_wrapper('BT ACL Sniff 1.28s interval Master @ 0dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_0-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_acl_sniff_1dot28s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_data_frame_list = test_case_wrapper('BT ACL Sniff 1.28s interval Master @ 4dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_4-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_acl_sniff_1dot28s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_data_frame_list = test_case_wrapper('BT ACL Sniff 1.28s interval Master @ Max dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_1.28s_Master_Max-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_acl_sniff_1dot28s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')

			joined_data_frame_list = test_case_wrapper('BT ACL Sniff 0.5s interval Master @ 0 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_0-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_acl_sniff_0dot5s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_data_frame_list = test_case_wrapper('BT ACL Sniff 0.5s interval Master @ 4 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_4-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_acl_sniff_0dot5s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_data_frame_list = test_case_wrapper('BT ACL Sniff 0.5s interval Master @ Max dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_ACL_Sniff_0.5s_Master_Max-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_acl_sniff_0dot5s_master,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')

			joined_data_frame_list = test_case_wrapper('BT SCO HV3 Master @ 0 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_SCO_HV3_Master_0-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_sco_hv3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_data_frame_list = test_case_wrapper('BT SCO HV3 Master @ 4 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_SCO_HV3_Master_4-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_sco_hv3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_data_frame_list = test_case_wrapper('BT SCO HV3 Master @ Max dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_SCO_HV3_Master_Max-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_sco_hv3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')

			joined_data_frame_list = test_case_wrapper('BT SCO EV3 Master @ 0 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_SCO_EV3_Master_0-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_sco_ev3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_data_frame_list = test_case_wrapper('BT SCO EV3 Master @ 4 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_SCO_EV3_Master_4-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_sco_ev3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_data_frame_list = test_case_wrapper('BT SCO EV3 Master @ Max dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BT_SCO_EV3_Master_Max-dBm-pin'),
			                                           my_ssh_send_cmd.cc_bt_sco_ev3,
			                                           dut, dut_bd_addr,
			                                           ref, ref_bd_addr,
			                                           'Max')
		elif str(config['Test_Case'].get('BT_Enable')) == '0':
			print('Skip all BT test cases')
		else:
			print('Invalid "BT_Enable" info, pls check config.ini file. Exiting...')
			sys.exit(1)

		if str(config['Test_Case'].get('BLE_Enable')) == '1':
			joined_data_frame_list = test_case_wrapper('BLE Adv 1.28s interval 3 channels @ 0 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Adv_1.28s_3Channel_0-dBm-pin'),
			                                           my_ssh_send_cmd.cc_ble_adv_1dot28s_3channel,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_data_frame_list = test_case_wrapper('BLE Adv 1.28s interval 3 channels @ 4 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Adv_1.28s_3Channel_4-dBm-pin'),
			                                           my_ssh_send_cmd.cc_ble_adv_1dot28s_3channel,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_data_frame_list = test_case_wrapper('BLE Adv 1.28s interval 3 channels @ Max dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Adv_1.28s_3Channel_Max-dBm-pin'),
			                                           my_ssh_send_cmd.cc_ble_adv_1dot28s_3channel,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_data_frame_list = test_case_wrapper('BLE Scan 1.28s interval',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Scan_1.28s'),
			                                           my_ssh_send_cmd.cc_ble_scan_1dot28s,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_data_frame_list = test_case_wrapper('BLE Scan 1s interval',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Scan_1s'),
			                                           my_ssh_send_cmd.cc_ble_scan_1s,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_data_frame_list = test_case_wrapper('BLE Scan 10ms interval',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Scan_10ms'),
			                                           my_ssh_send_cmd.cc_ble_scan_10ms,
			                                           dut,
			                                           ref,
			                                           '0', 1)

			joined_data_frame_list = test_case_wrapper('BLE Connection 1.28s interval @ 0 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Connection_1.28s_0-dBm-pin'),
			                                           my_ssh_send_cmd.cc_ble_connection_1dot28s,
			                                           dut,
			                                           ref, ref_bd_addr,
			                                           '0')

			joined_data_frame_list = test_case_wrapper('BLE Connection 1.28s interval @ 4 dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Connection_1.28s_4-dBm-pin'),
			                                           my_ssh_send_cmd.cc_ble_connection_1dot28s,
			                                           dut,
			                                           ref, ref_bd_addr,
			                                           '4')

			joined_data_frame_list = test_case_wrapper('BLE Connection 1.28s interval @ Max dBm at Pin',
			                                           joined_data_frame_list,
			                                           config['Test_Case'].get('BLE_Connection_1.28s_Max-dBm-pin'),
			                                           my_ssh_send_cmd.cc_ble_connection_1dot28s,
			                                           dut,
			                                           ref, ref_bd_addr,
			                                           'Max')
		elif str(config['Test_Case'].get('BLE_Enable')) == '0':
			print('Skip all BLE test cases')
		else:
			print('Invalid "BLE_Enable" info, pls check config.ini file')
			sys.exit(1)

	# print(joined_data_frame_list)

	# Write to different sheet
	excel_sheet_name_list = [str(config['BASIC'].get('Excel_Sheet_Name_A')),
	                         str(config['BASIC'].get('Excel_Sheet_Name_B')),
	                         str(config['BASIC'].get('Excel_Sheet_Name_C')),
	                         str(config['BASIC'].get('Excel_Sheet_Name_D')), ]

	my_excel_obj = my_excel.open_excel('test.xlsx')

	for i in range(len(visa_address())):
		# Convert the dataframe to an XlsxWriter Excel object.
		my_excel.write_excel(my_excel_obj, joined_data_frame_list[i], excel_sheet_name_list[i])

	my_excel.close_excel(my_excel_obj)

	end_time = ender()
	run_time(start_time, end_time)
