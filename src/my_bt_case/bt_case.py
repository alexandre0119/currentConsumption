#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Alex Wang

import src.my_config.config_basic as config_basic
from src.my_misc.my_logging import create_logger
from src.my_misc.my_decorator import enter_hci_header_footer

config = config_basic.load_config()
log = create_logger()


class Init(object):
	def __init__(self, chip_version, hci_dut, hci_ref):
		self.chip_version = str(chip_version)
		self.hci_dut = hci_dut
		self.hci_ref = hci_ref


class PowerLevel(Init):
	def __init__(self, chip_version, hci_dut, hci_ref):
		Init.__init__(self, chip_version, hci_dut, hci_ref)
		self.chip_version = str(chip_version)
		self.hci_dut = hci_dut
		self.hci_ref = hci_ref
		self.bt_power_index = {'8977':
			                       {'0': config_basic.config_bt_power('8977', '0'),
			                        '4': config_basic.config_bt_power('8977', '4'),
			                        'Max': config_basic.config_bt_power('8977', 'Max')},
		                       '8997':
			                       {'0': config_basic.config_bt_power('8997', '0'),
			                        '4': config_basic.config_bt_power('8997', '4'),
			                        'Max': config_basic.config_bt_power('8997', 'Max')},
		                       '8987':
			                       {'0': config_basic.config_bt_power('8987', '0'),
			                        '4': config_basic.config_bt_power('8987', '4'),
			                        'Max': config_basic.config_bt_power('8987', 'Max')}
		                       }

	@enter_hci_header_footer()
	def bt_set_power_level(self, power_level):
		set_power = ''
		power_level = str(power_level)
		# log.info(self.chip_version, type(self.chip_version), '$$$$$$$$$$$$$$$$$$$$$$')

		if self.chip_version == '8977':
			# log.info('Enter here!!!!!!!!!!!!!!!!')
			if power_level == '0':
				set_power = self.bt_power_index[self.chip_version]['0']
			# print(set_power, '$$$$$$$$$$$$$$$$$$$$$$')
			elif power_level == '4':
				set_power = self.bt_power_index[self.chip_version]['4']
			elif power_level == 'Max':
				set_power = self.bt_power_index[self.chip_version]['Max']
			else:
				log.info('Invalid input power level')
		elif self.chip_version == '8997':
			if power_level == '0':
				set_power = self.bt_power_index[self.chip_version]['0']
			# print(set_power, '$$$$$$$$$$$$$$$$$$$$$$')
			elif power_level == '4':
				set_power = self.bt_power_index[self.chip_version]['4']
			elif power_level == 'Max':
				set_power = self.bt_power_index[self.chip_version]['Max']
			else:
				log.info('Invalid input power level')
		elif self.chip_version == '8987':
			if power_level == '0':
				set_power = self.bt_power_index[self.chip_version]['0']
			# print(set_power, '$$$$$$$$$$$$$$$$$$$$$$')
			elif power_level == '4':
				set_power = self.bt_power_index[self.chip_version]['4']
			elif power_level == 'Max':
				set_power = self.bt_power_index[self.chip_version]['Max']
			else:
				log.info('Invalid input power level')
		else:
			log.info('Invalid chip version, pls check config.ini file')

		cmd = 'hcitool -i {0} cmd 3F 64 9F 01 01 04 00 00 00 00 00 00\n' \
		      'sleep 1\n' \
		      'hcitool -i {1} cmd 3F 64 B1 01 01 {2} 00 00 00 00 00 00'.format(self.hci_dut, self.hci_dut, set_power)
		log.info(cmd)
		return cmd


class BT(Init):
	def __init__(self, chip_version, hci_dut, hci_ref):
		Init.__init__(self, chip_version, hci_dut, hci_ref)
		self.chip_version = str(chip_version)
		self.hci_dut = hci_dut
		self.hci_ref = hci_ref

	@enter_hci_header_footer()
	def bt_reset(self, hci_interface):
		cmd = 'hciconfig {0} reset'.format(hci_interface)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_deepsleep(self):
		cmd = 'hcitool -i {0} cmd 3F 23 02'.format(self.hci_dut)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_idle(self):
		cmd = 'hcitool -i {0} cmd 3F 23 01'.format(self.hci_dut)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_noscan(self):
		cmd = 'hciconfig {0} noscan'.format(self.hci_dut)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_pscan(self):
		cmd = 'hciconfig {0} pscan'.format(self.hci_dut)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_iscan(self):
		cmd = 'hciconfig {0} iscan'.format(self.hci_dut)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_piscan(self):
		cmd = 'hciconfig {0} piscan'.format(self.hci_dut)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_acl_sniff_1dot28s_master(self, dut_address, ref_address):
		dut_address = str(dut_address).strip().split(':')
		dut_address = ':'.join(dut_address)
		# print(dut_address, '~~~~~~~~~~~~~~~~~~~~')

		ref_address = str(ref_address).strip().split(':')
		ref_address = ':'.join(ref_address)

		cmd = 'hcitool -i {0} cc --role=m {3}\n' \
		      'sleep 1\n' \
		      'hcitool -i {0} hcon -t acl {3}\n' \
		      'sleep 1\n' \
		      'hcitool -i {1} hcon -t acl {2}\n' \
		      'sleep 2\n' \
		      'hcitool -i {0} sniff {3} 0x0800 0x0800 0x01 0x00' \
			.format(self.hci_dut, self.hci_ref, dut_address, ref_address)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_acl_sniff_0dot5s_master(self, dut_address, ref_address):
		dut_address = str(dut_address).strip().split(':')
		dut_address = ':'.join(dut_address)
		# print(dut_address, '~~~~~~~~~~~~~~~~~~~~')

		ref_address = str(ref_address).strip().split(':')
		ref_address = ':'.join(ref_address)

		cmd = 'hcitool -i {0} cc --role=m {3}\n' \
		      'sleep 1\n' \
		      'hcitool -i {0} hcon -t acl {3}\n' \
		      'sleep 1\n' \
		      'hcitool -i {1} hcon -t acl {2}\n' \
		      'sleep 2\n' \
		      'hcitool -i {0} sniff {3} 0x0320 0x0320 0x01 0x00' \
			.format(self.hci_dut, self.hci_ref, dut_address, ref_address)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_sco_hv3(self, ref_address):
		ref_address = str(ref_address).strip().split(':')
		ref_address = ':'.join(ref_address)

		cmd = 'hcitool -i {0} scc {1} 1F40 1F40 0007 60 00 03C4' \
			.format(self.hci_dut, ref_address)
		log.info(cmd)
		return cmd

	@enter_hci_header_footer()
	def bt_sco_ev3(self, ref_address):
		ref_address = str(ref_address).strip().split(':')
		ref_address = ':'.join(ref_address)

		cmd = 'hcitool -i {0} scc {1} 1F40 1F40 0007 60 00 03C8' \
			.format(self.hci_dut, ref_address)
		log.info(cmd)
		return cmd


class BLE(Init):
	def __init__(self, chip_version, hci_dut, hci_ref):
		Init.__init__(self, chip_version, hci_dut, hci_ref)
		self.chip_version = str(chip_version)
		self.hci_dut = hci_dut
		self.hci_ref = hci_ref

	@enter_hci_header_footer()
	def ble_adv_1dot28s_3channel(self, enable):
		if str(enable) == '1':
			cmd = 'hcitool -i {0} cmd 08 06 00 08 00 08 03 00 00 BC 9A 78 56 34 12 07 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 08 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 0x08 0x0A 0x0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		elif str(enable) == '0':
			cmd = 'hcitool -i {0} cmd 08 06 00 08 00 08 03 00 00 BC 9A 78 56 34 12 07 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 08 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 0x08 0x0A 0x0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		else:
			log.info('Invalid input for BLE Adv setting, pls check config.ini file')

	@enter_hci_header_footer()
	def ble_scan_1dot28s(self, enable):
		if str(enable) == '1':
			cmd = 'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0B 01 00 08 10 00 00 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0C 01 0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		elif str(enable) == '0':
			cmd = 'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0B 01 00 08 10 00 00 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0C 01 0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		else:
			log.info('Invalid input for BLE Adv setting, pls check config.ini file')

	@enter_hci_header_footer()
	def ble_scan_1s(self, enable):
		if str(enable) == '1':
			cmd = 'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0B 01 40 06 10 00 00 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0C 01 0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		elif str(enable) == '0':
			cmd = 'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0B 01 40 06 10 00 00 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0C 01 0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		else:
			log.info('Invalid input for BLE Adv setting, pls check config.ini file')

	@enter_hci_header_footer()
	def ble_scan_10ms(self, enable):
		if str(enable) == '1':
			cmd = 'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0B 01 10 00 10 00 00 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0C 01 0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		elif str(enable) == '0':
			cmd = 'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
			      '99 88 77 66 55 44 33 22 11 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0B 01 10 00 10 00 00 00\n' \
			      'sleep 1\n' \
			      'hcitool -i {0} cmd 08 0C 01 0{1}' \
				.format(self.hci_dut, enable)
			log.info(cmd)
			return cmd
		else:
			log.info('Invalid input for BLE Adv setting, pls check config.ini file')

	@enter_hci_header_footer()
	def ble_connection_1dot28s(self, ref_address):
		ref_address = str(ref_address).strip().split(':')
		ref_address.reverse()
		ref_address = ' '.join(ref_address)
		# print(ref_address, '!!!!!!!!!!!!!!!!!!!!!!')
		cmd = 'hcitool -i {1} cmd 08 06 00 08 00 08 00 00 00 BC 9A 78 56 34 12 07 00\n' \
		      'sleep 1\n' \
		      'hcitool -i {1} cmd 08 08 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
		      '99 88 77 66 55 44 33 22 11 00\n' \
		      'sleep 1\n' \
		      'hcitool -i {1} cmd 0x08 0x0A 0x01\n' \
		      'sleep 1\n' \
		      'hcitool -i {0} cmd 08 09 1F 00 99 88 77 66 55 44 33 22 11 00 99 88 77 66 55 44 33 22 11 00 ' \
		      '99 88 77 66 55 44 33 22 11 00\n' \
		      'sleep 1\n' \
		      'hcitool -i {0} cmd 08 0B 01 10 00 10 00 00 00\n' \
		      'sleep 1\n' \
		      'hcitool -i {0} cmd 08 0C 01 01\n' \
		      'sleep 2\n' \
		      'hcitool -i {0} cmd 08 0C 01 00\n' \
		      'sleep 2\n' \
		      'hcitool -i {0} cmd 08 0D 10 00 10 00 00 00 {2} 00 00 04 00 04 00 00 00 08 10 00 10 00\n' \
		      'sleep 2\n' \
		      'hcitool -i {0} cmd 08 13 80 00 00 04 00 04 00 00 00 08 10 00 10 00' \
			.format(self.hci_dut, self.hci_ref, ref_address)
		log.info(cmd)
		return cmd