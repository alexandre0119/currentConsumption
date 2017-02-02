#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import re

from paramiko import client

import src.my_config as my_config
from src.my_bt_case import *

config = configparser.ConfigParser()
config.read('config.ini')
enable_robin3_8977 = str(config['Test_Case'].get('Enable'))


class SSH:
	client = None
	shell = None
	transport = None

	def __init__(self, address, username, password):
		self.address = address
		self.username = username
		self.userPassword = password
		self.rootPassword = password
		print("Connecting to server on ip address", str(self.address))
		self.client = client.SSHClient()
		self.client.set_missing_host_key_policy(client.AutoAddPolicy())
		self.client.connect(self.address, username=self.username, password=self.userPassword, look_for_keys=False)

	def send_command(self, command):
		if self.client:
			stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
			# stdin, stdout, stderr = self.client.exec_command('sudo ' + command)
			# stdin.write(self.rootPassword + '\n')
			stdin.flush()
			stdin.close()
			data = stdout.read().splitlines()
			error = stderr.read().splitlines()
			# data = stdout.readlines()
			# logger_append.info(data)
			data_return = []
			error_return = []
			for line in data:
				print(str(line, 'utf8'))
				# logger_append.info(str(line, 'utf8'))
				data_return.append(str(line, 'utf8'))
			# print(data_return)
			for line in error:
				print(str(line, 'utf8'))
				error_return.append(str(line, 'utf8'))
			while not stdout.channel.exit_status_ready():
				# Print data when available
				if stdout.channel.recv_ready():
					alldata = stdout.channel.recv(1024)
					prevdata = b"1"
					while prevdata:
						prevdata = stdout.channel.recv(1024)
						alldata += prevdata
					print(str(alldata, "utf8"))
			return data_return, error_return
		else:
			print("Connection not opened.")


def open_connection_ssh():
	"""
	Open SSH connection based on server, username and password
	:return: SSH connection
	"""
	ssh_server = my_config.config_ssh_server()
	ssh_username = my_config.config_ssh_username()
	ssh_password = my_config.config_ssh_password()
	connection = SSH(ssh_server, ssh_username, ssh_password)
	return connection


def get_hci_bd_address():
	data = open_connection_ssh().send_command('hciconfig')[0]
	print('!!!!!!!!!!!!!!!!', open_connection_ssh().send_command('hciconfig'))
	# logger_append.info(data)
	regex_bd_address = re.compile(r'[\s]*BD Address:[\s]*' +
	                              r'(?P<bd_address>[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+)')
	regex_hci = re.compile(r'[\s]?(?P<hci>hci[0-9]+):')
	bd_addr_list = []
	for line_number in range(len(data)):
		line_content = data[line_number]
		match_hci = regex_hci.match(line_content)
		if match_hci:
			# logger_append.info('Match found: {0}'.format(match_hci.group('hci')))
			line_number += 1
			line_content = data[line_number]
			match_bd_address = regex_bd_address.match(line_content)
			if match_bd_address:
				# logger_append.info('Match found: {0}'.format(match_bd_address.group('bd_address')))
				bd_addr_list.append({
					match_hci.group('hci').strip(): match_bd_address.group('bd_address').strip()})
	# logger_append.info(bd_addr_list)
	return bd_addr_list



# def cc_bt_acl_sniff_1dot28s_master(dut_address, ref_address):
# 	open_connection_ssh().send_command(bt.bt_acl_sniff_1dot28s_master(dut_address, ref_address))

#
# def cc_bt_acl_sniff_0dot5s_master(dut_address, ref_address):
# 	open_connection_ssh().send_command(bt.bt_acl_sniff_0dot5s_master(dut_address, ref_address))
#
#
# def cc_bt_sco_hv3(ref_address):
# 	open_connection_ssh().send_command(bt.bt_sco_hv3(ref_address))
#
#
# def cc_bt_sco_ev3(ref_address):
# 	open_connection_ssh().send_command(bt.bt_sco_ev3(ref_address))
#
#
# def cc_ble_adv_1dot28s_3channel(enable):
# 	open_connection_ssh().send_command(ble.ble_adv_1dot28s_3channel(enable))
#
#
# def cc_ble_scan_1dot28s(enable):
# 	open_connection_ssh().send_command(ble.ble_scan_1dot28s(enable))
#
#
# def cc_ble_scan_1s(enable):
# 	open_connection_ssh().send_command(ble.ble_scan_1s(enable))
#
#
# def cc_ble_scan_10ms(enable):
# 	open_connection_ssh().send_command(ble.ble_scan_10ms(enable))
#
#
# def cc_ble_connection_1dot28s(ref_address):
# 	open_connection_ssh().send_command(ble.ble_connection_1dot28s(ref_address))


"""
I finally figured out that .execute_command() is basically a single session,
so doing a .execute_command('cd scripts') and then executing the script with
another .execute_command() reverts back to your default directory.
The alternatives are to send all the commands at once separated
by a ; .execute_command('cd scripts; ./myscript.sh'),
or to use the .interactive() shell support.
Since I only needed to fire off this script I used the first solution.
"""
