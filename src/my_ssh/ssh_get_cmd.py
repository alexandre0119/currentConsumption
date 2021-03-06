#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_ssh.ssh_basic as ssh_basic
import src.my_config.config_basic as config_basic
import sys
import re


def get_bd_addr_list():
	"""
	Get BD addr list
	:return: BD addr list
	"""
	data = ssh_basic.open_connection_ssh().send_command('hciconfig')[0]

	regex_bd_address = re.compile(r'[\s]*BD Address:[\s]*' +
	                              r'(?P<bd_address>[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+)')
	regex_hci = re.compile(r'[\s]?(?P<hci>hci[0-9]+):')

	bd_addr_list = []
	for line_number in range(len(data)):
		line_content = data[line_number]
		match_hci = regex_hci.match(line_content)
		if match_hci:
			# print('Match found: {0}'.format(match_hci.group('hci')))
			line_number += 1
			line_content = data[line_number]
			match_bd_address = regex_bd_address.match(line_content)
			if match_bd_address:
				# print('Match found: {0}'.format(match_bd_address.group('bd_address')))
				bd_addr_list.append({
					match_hci.group('hci').strip(): match_bd_address.group('bd_address').strip()})
	return bd_addr_list


def bd_addr():
	"""
	Convert BD addr list to DUT and Ref BD addresses
	:return: [0] DUT BD addr; [1] Ref BD addr
	"""
	dut_bd_address = ''
	ref_bd_address = ''
	config = config_basic.load_config()
	for i in get_bd_addr_list():
		# print(i.keys(), i.values())
		for j, k in i.items():
			if j == config['BASIC'].get('Dut'):
				dut_bd_address = k
			elif j == config['BASIC'].get('Ref'):
				ref_bd_address = k
			else:
				print('Something wrong with BD address. Exciting....')
				sys.exit(1)
	return dut_bd_address, ref_bd_address
