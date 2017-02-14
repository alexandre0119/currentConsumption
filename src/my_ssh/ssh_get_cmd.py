#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_ssh.ssh_basic as ssh_basic
import src.my_config as my_config
import sys
import re


def get_bd_addr_list():
	data = ssh_basic.open_connection_ssh().send_command('hciconfig')[0]

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
	return bd_addr_list


def bd_addr():
	dut_bd_address = ''
	ref_bd_address = ''
	config = my_config.load_config('config.ini')
	for i in get_bd_addr_list():
		# print(i.keys(), i.values(), '!!!!!!!!!!!!!!!!!!!!!!')
		for j, k in i.items():
			if j == config['BASIC'].get('Dut'):
				dut_bd_address = k
			elif j == config['BASIC'].get('Ref'):
				ref_bd_address = k
			else:
				print('Something wrong with BD address. Exciting....')
				sys.exit(1)
	return dut_bd_address, ref_bd_address
