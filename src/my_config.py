#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import configparser


def load_config(config_name='config.ini'):
	"""
	Load config.ini file and return instance
	:param config_name: config.ini file name
	:return: config instance
	"""
	config = configparser.ConfigParser()
	config.read(config_name)
	return config


def config_chip_version():
	"""
	Load chip version from config.ini
	:return: chip version string
	"""
	config = load_config('config.ini')
	chip_version = str(config['BASIC'].get('Chip_Version'))
	return chip_version


def config_dut():
	"""
	Load DUT hci# from config.ini
	:return: DUT hci# string
	"""
	config = load_config('config.ini')
	dut = str(config['BASIC'].get('Dut'))
	return dut


def config_ref():
	"""
	Load REF hci# from config.ini
	:return: REF hci# string
	"""
	config = load_config('config.ini')
	ref = str(config['BASIC'].get('Ref'))
	return ref


def config_ssh_server():
	"""
	Load SSH server(destination) IP address from config.ini
	:return: SSH destination IP address string
	"""
	config = load_config('config.ini')
	ssh_server = str(config['SSH'].get('SSH_Server'))
	return ssh_server


def config_ssh_username():
	"""
	Load SSH server(destination) login username from config.ini
	:return: SSH destination login username string
	"""
	config = load_config('config.ini')
	ssh_username = str(config['SSH'].get('SSH_Username'))
	return ssh_username


def config_ssh_password():
	"""
	Load SSH server(destination) login password from config.ini
	:return: SSH destination login password string
	"""
	config = load_config('config.ini')
	ssh_password = str(config['SSH'].get('SSH_Password'))
	return ssh_password