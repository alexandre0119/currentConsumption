#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import configparser
from src.my_misc.my_logging import create_logger
log = create_logger()

def load_config():
	"""
	Load config.ini file and return instance
	:param config_name: config.ini file name
	:return: config instance
	"""
	config = configparser.ConfigParser()
	config_file_name = 'config.ini'
	config.read(config_file_name)
	return config


def config_chip_version():
	"""
	Load chip version from config.ini
	:return: chip version string
	"""
	config = load_config()
	chip_version = str(config['BASIC'].get('Chip_Version'))
	return chip_version


def config_dut():
	"""
	Load DUT hci# from config.ini
	:return: DUT hci# string
	"""
	config = load_config()
	dut = str(config['BASIC'].get('Dut'))
	return dut


def config_ref():
	"""
	Load REF hci# from config.ini
	:return: REF hci# string
	"""
	config = load_config()
	ref = str(config['BASIC'].get('Ref'))
	return ref


def config_ssh_server():
	"""
	Load SSH server(destination) IP address from config.ini
	:return: SSH destination IP address string
	"""
	config = load_config()
	ssh_server = str(config['SSH'].get('SSH_Server'))
	return ssh_server


def config_ssh_username():
	"""
	Load SSH server(destination) login username from config.ini
	:return: SSH destination login username string
	"""
	config = load_config()
	ssh_username = str(config['SSH'].get('SSH_Username'))
	return ssh_username


def config_ssh_password():
	"""
	Load SSH server(destination) login password from config.ini
	:return: SSH destination login password string
	"""
	config = load_config()
	ssh_password = str(config['SSH'].get('SSH_Password'))
	return ssh_password


def config_bt_power(chip_version, bt_power_level):
	config = load_config()
	if chip_version == '8977':
		if bt_power_level == '0':
			bt_power_index = str(config['Robin3_8977_Power_Index'].get('0_dBm_Pin'))
			return bt_power_index
		elif bt_power_level == '4':
			bt_power_index = str(config['Robin3_8977_Power_Index'].get('4_dBm_Pin'))
			return bt_power_index
		elif bt_power_level == 'Max':
			bt_power_index = str(config['Robin3_8977_Power_Index'].get('Max_dBm_Pin'))
			return bt_power_index
		else:
			log.info('Something wrong with BT power level setting')
	elif chip_version == '8997':
		if bt_power_level == '0':
			bt_power_index = str(config['KF2_8997_Power_Index'].get('0_dBm_Pin'))
			return bt_power_index
		elif bt_power_level == '4':
			bt_power_index = str(config['KF2_8997_Power_Index'].get('4_dBm_Pin'))
			return bt_power_index
		elif bt_power_level == 'Max':
			bt_power_index = str(config['KF2_8997_Power_Index'].get('Max_dBm_Pin'))
			return bt_power_index
		else:
			log.info('Something wrong with BT power level setting')
	elif chip_version == '8987':
		if bt_power_level == '0':
			bt_power_index = str(config['CA2_8987_Power_Index'].get('0_dBm_Pin'))
			return bt_power_index
		elif bt_power_level == '4':
			bt_power_index = str(config['CA2_8987_Power_Index'].get('4_dBm_Pin'))
			return bt_power_index
		elif bt_power_level == 'Max':
			bt_power_index = str(config['CA2_8987_Power_Index'].get('Max_dBm_Pin'))
			return bt_power_index
		else:
			log.info('Something wrong with BT power level setting')
	else:
		log.info('Something wrong with chip version select for BT power level')